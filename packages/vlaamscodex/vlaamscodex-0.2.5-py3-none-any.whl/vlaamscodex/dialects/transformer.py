"""Dialect Transformation Engine for VlaamsCodex.

This module provides rule-based text transformation to convert standard
Dutch/Flemish text into regional dialect variants. It powers the multi-dialect
CLI experience and can be used standalone for text transformation.

Key Features:
- 83 dialect packs covering 7 Flemish regions
- Rule types: word replacement, regex patterns, particle insertion
- Inheritance chains for rule reuse
- Protected terms system to preserve legal/modality words
- Deterministic mode for reproducible transforms

Environment Variables:
    VLAAMSCODEX_DIALECTS_DIR: Override dialect packs location
    VLAAMSCODEX_DIALECT_DETERMINISTIC: Enable deterministic mode (default: True)
    VLAAMSCODEX_DIALECT_SEED: Seed for deterministic randomness (default: 0)
    VLAAMSCODEX_DIALECT_PARTICLES: Enable particle insertion (default: False)
    VLAAMSCODEX_PRONOUN_*: Override default pronouns (ge/u/uw)

Example:
    >>> from vlaamscodex.dialects.transformer import transform, available_packs
    >>> text = "Gij moet dat niet doen."
    >>> transform(text, "antwerps/stad")
    'Ge moet da nie dansen.'
    >>> [p.id for p in available_packs()[:3]]
    ['algemeen-vlaams', 'antwerps', 'antwerps/haven']
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping


GLOBAL_PROTECTED_TERMS: tuple[str, ...] = (
    # Legal modality / conditions (must not drift)
    "verplicht",
    "verboden",
    "mag",
    "moet",
    "kan",
    "niet",
    "geen",
    "tenzij",
    "enkel",
    "alleen",
    "behalve",
    "uitzondering",
    "boete",
    "straf",
    # Common plural forms (defensive)
    "uitzonderingen",
    "boetes",
    "straffen",
)


@dataclass(frozen=True, slots=True)
class PackInfo:
    id: str
    label: str
    inherits: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class DialectTransformConfig:
    deterministic: bool = True
    seed: int = 0
    enable_particles: bool = False
    pronoun_subject: str = "ge"
    pronoun_object: str = "u"
    pronoun_possessive: str = "uw"
    max_passes: int = 3
    strict_idempotency: bool = False


def _env_bool(name: str, default: bool) -> bool:
    """Parse a boolean environment variable with flexible input handling."""
    raw = os.getenv(name)
    if raw is None:
        return default
    raw = raw.strip().lower()
    if raw in ("1", "true", "yes", "y", "on"):
        return True
    if raw in ("0", "false", "no", "n", "off"):
        return False
    return default


def _env_int(name: str, default: int) -> int:
    """Parse an integer environment variable with fallback."""
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw.strip())
    except ValueError:
        return default


def _env_str(name: str, default: str) -> str:
    """Parse a string environment variable with fallback."""
    raw = os.getenv(name)
    if raw is None:
        return default
    raw = raw.strip()
    return raw or default


def _default_config() -> DialectTransformConfig:
    """Build default config from environment variables."""
    return DialectTransformConfig(
        deterministic=_env_bool("VLAAMSCODEX_DIALECT_DETERMINISTIC", True),
        seed=_env_int("VLAAMSCODEX_DIALECT_SEED", 0),
        enable_particles=_env_bool("VLAAMSCODEX_DIALECT_PARTICLES", False),
        pronoun_subject=_env_str("VLAAMSCODEX_PRONOUN_SUBJECT", "ge"),
        pronoun_object=_env_str("VLAAMSCODEX_PRONOUN_OBJECT", "u"),
        pronoun_possessive=_env_str("VLAAMSCODEX_PRONOUN_POSSESSIVE", "uw"),
        max_passes=_env_int("VLAAMSCODEX_DIALECT_MAX_PASSES", 3),
        strict_idempotency=_env_bool("VLAAMSCODEX_DIALECT_STRICT_IDEMPOTENCY", False),
    )


def _find_dialects_dir() -> Path:
    """Locate the dialects directory containing pack definitions.

    Resolution order:
    1. VLAAMSCODEX_DIALECTS_DIR environment variable
    2. Walk up from this file to find dialects/index.json (dev mode)

    Raises:
        FileNotFoundError: If dialects directory cannot be found.
    """
    env = os.getenv("VLAAMSCODEX_DIALECTS_DIR")
    if env:
        return Path(env).expanduser().resolve()

    # Dev/repo mode: walk upwards until we find dialects/index.json
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "dialects" / "index.json"
        if candidate.exists():
            return candidate.parent

    raise FileNotFoundError(
        "Could not find dialects directory. Set VLAAMSCODEX_DIALECTS_DIR or run from repo checkout."
    )


def _pack_filename(dialect_id: str) -> str:
    """Convert dialect ID to filename (e.g., 'west-vlaams/kust' -> 'west-vlaams__kust.json')."""
    return f"{dialect_id.replace('/', '__')}.json"


def _apply_leading_case(dst: str, src: str) -> str:
    """Apply the case pattern from src to dst (preserve leading uppercase/full-caps)."""
    if not src:
        return dst
    if src.isupper():
        return dst.upper()
    if src[0].isupper() and dst:
        return dst[0].upper() + dst[1:]
    return dst


def _expand_vars(template: str, config: DialectTransformConfig) -> str:
    return (
        template.replace("{pronoun_subject}", config.pronoun_subject)
        .replace("{pronoun_object}", config.pronoun_object)
        .replace("{pronoun_possessive}", config.pronoun_possessive)
    )


_SENTENCE_PUNCT_RE = re.compile(r"[.!?]+")


def _iter_sentence_spans(text: str) -> Iterable[tuple[int, int, bool]]:
    """
    Yield (start, end, is_question) spans. Each span includes trailing whitespace after punctuation.
    If no punctuation is found, yields a single span for the whole text.
    """
    start = 0
    found = False
    for m in _SENTENCE_PUNCT_RE.finditer(text):
        found = True
        punct_end = m.end()
        is_question = "?" in m.group(0)
        end = punct_end
        while end < len(text) and text[end].isspace():
            end += 1
        yield start, end, is_question
        start = end
    if not found and text:
        yield 0, len(text), False
    elif start < len(text):
        yield start, len(text), False


def _hash_float_0_1(key: str) -> float:
    h = hashlib.sha256(key.encode("utf-8")).digest()
    x = int.from_bytes(h[:8], "big", signed=False)
    return x / 2**64


def _build_protected_pattern(terms: Iterable[str]) -> re.Pattern[str] | None:
    pats: list[str] = []
    for term in terms:
        t = term.strip()
        if not t:
            continue
        parts = t.split()
        if len(parts) == 1:
            pats.append(rf"\b{re.escape(parts[0])}\b")
        else:
            inner = r"\s+".join(rf"\b{re.escape(p)}\b" for p in parts)
            pats.append(inner)
    if not pats:
        return None
    # Longest first to prefer phrases over single words.
    pats.sort(key=len, reverse=True)
    return re.compile(r"|".join(f"(?:{p})" for p in pats), flags=re.IGNORECASE)


def _mask_protected(text: str, protected_terms: Iterable[str]) -> tuple[str, dict[str, str]]:
    pat = _build_protected_pattern(protected_terms)
    if pat is None:
        return text, {}

    mapping: dict[str, str] = {}
    counter = 0

    def repl(m: re.Match[str]) -> str:
        nonlocal counter
        placeholder = f"\uE000{counter}\uE001"
        mapping[placeholder] = m.group(0)
        counter += 1
        return placeholder

    return pat.sub(repl, text), mapping


def _unmask(text: str, mapping: Mapping[str, str]) -> str:
    if not mapping:
        return text
    # Placeholders are unique; simple replace is fine.
    for placeholder, original in mapping.items():
        text = text.replace(placeholder, original)
    return text


@dataclass(frozen=True, slots=True)
class _LoadedPack:
    id: str
    label: str
    inherits: tuple[str, ...]
    protected_terms: tuple[str, ...]
    rules: tuple[dict[str, Any], ...]


@dataclass(frozen=True, slots=True)
class _ResolvedPack:
    id: str
    label: str
    inherits: tuple[str, ...]
    protected_terms: tuple[str, ...]
    rules: tuple[dict[str, Any], ...]


class _DialectRegistry:
    def __init__(self, dialects_dir: Path | None = None) -> None:
        self.dialects_dir = dialects_dir or _find_dialects_dir()
        self.index_path = self.dialects_dir / "index.json"
        self.packs_dir = self.dialects_dir / "packs"
        self._index: dict[str, dict[str, Any]] | None = None
        self._loaded: dict[str, _LoadedPack] = {}
        self._resolved: dict[str, _ResolvedPack] = {}

    def _load_index(self) -> dict[str, dict[str, Any]]:
        if self._index is not None:
            return self._index
        data = json.loads(self.index_path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("dialects/index.json must be a list")
        index: dict[str, dict[str, Any]] = {}
        for entry in data:
            if not isinstance(entry, dict):
                raise ValueError("dialects/index.json entries must be objects")
            dialect_id = entry.get("id")
            if not isinstance(dialect_id, str) or not dialect_id:
                raise ValueError("dialects/index.json entry missing string 'id'")
            if dialect_id in index:
                raise ValueError(f"Duplicate dialect id in index: {dialect_id}")
            index[dialect_id] = entry
        self._index = index
        return index

    def available(self) -> list[PackInfo]:
        idx = self._load_index()
        packs: list[PackInfo] = []
        for dialect_id, entry in idx.items():
            label = entry.get("label", dialect_id)
            inherits = entry.get("inherits", [])
            if not isinstance(label, str):
                label = dialect_id
            if not isinstance(inherits, list) or not all(isinstance(x, str) for x in inherits):
                inherits = []
            packs.append(PackInfo(id=dialect_id, label=label, inherits=tuple(inherits)))
        packs.sort(key=lambda p: p.id)
        return packs

    def _pack_path(self, dialect_id: str) -> Path:
        entry = self._load_index().get(dialect_id)
        if entry is None:
            raise KeyError(dialect_id)
        filename = entry.get("file")
        if isinstance(filename, str) and filename:
            return self.packs_dir / filename
        return self.packs_dir / _pack_filename(dialect_id)

    def load(self, dialect_id: str) -> _LoadedPack:
        if dialect_id in self._loaded:
            return self._loaded[dialect_id]

        path = self._pack_path(dialect_id)
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError(f"Pack must be a JSON object: {path}")

        pack_id = data.get("id")
        if pack_id != dialect_id:
            raise ValueError(f"Pack id mismatch in {path}: expected {dialect_id!r}, got {pack_id!r}")

        label = data.get("label", dialect_id)
        if not isinstance(label, str) or not label:
            label = dialect_id

        inherits = data.get("inherits", [])
        if inherits is None:
            inherits = []
        if not isinstance(inherits, list) or not all(isinstance(x, str) for x in inherits):
            raise ValueError(f"Invalid 'inherits' in {path}")

        protected_terms = data.get("protected_terms", [])
        if not isinstance(protected_terms, list) or not all(isinstance(x, str) for x in protected_terms):
            raise ValueError(f"Invalid 'protected_terms' in {path}")

        rules = data.get("rules", [])
        if not isinstance(rules, list) or not all(isinstance(x, dict) for x in rules):
            raise ValueError(f"Invalid 'rules' in {path}")

        pack = _LoadedPack(
            id=dialect_id,
            label=label,
            inherits=tuple(inherits),
            protected_terms=tuple(protected_terms),
            rules=tuple(rules),
        )
        self._loaded[dialect_id] = pack
        return pack

    def resolve(self, dialect_id: str) -> _ResolvedPack:
        if dialect_id in self._resolved:
            return self._resolved[dialect_id]

        idx = self._load_index()
        if dialect_id not in idx:
            raise KeyError(dialect_id)

        visiting: set[str] = set()
        order: list[str] = []
        visited: set[str] = set()

        def dfs(pid: str) -> None:
            if pid in visited:
                return
            if pid in visiting:
                chain = " -> ".join([*visiting, pid])
                raise ValueError(f"Dialect inheritance cycle detected: {chain}")
            visiting.add(pid)
            p = self.load(pid)
            for parent in p.inherits:
                if parent not in idx:
                    raise ValueError(f"Unknown inherited pack: {pid} inherits {parent}")
                dfs(parent)
            visiting.remove(pid)
            visited.add(pid)
            order.append(pid)

        dfs(dialect_id)

        label = self.load(dialect_id).label
        inherits = self.load(dialect_id).inherits

        protected: list[str] = []
        rules: list[dict[str, Any]] = []
        for pid in order:
            p = self.load(pid)
            protected.extend(p.protected_terms)
            rules.extend(p.rules)

        resolved = _ResolvedPack(
            id=dialect_id,
            label=label,
            inherits=inherits,
            protected_terms=tuple(dict.fromkeys(protected)),  # stable unique
            rules=tuple(rules),
        )
        self._resolved[dialect_id] = resolved
        return resolved


_DEFAULT_REGISTRY = _DialectRegistry()


def available_packs() -> list[PackInfo]:
    return _DEFAULT_REGISTRY.available()


def _compile_rule(
    rule: Mapping[str, Any],
    *,
    config: DialectTransformConfig,
    dialect_id: str,
    rule_index: int,
) -> callable[[str], str]:
    rtype = rule.get("type")
    if rtype == "replace_word":
        src = rule.get("from")
        dst_template = rule.get("to")
        if not isinstance(src, str) or not src:
            raise ValueError("replace_word requires non-empty string 'from'")
        if not isinstance(dst_template, str):
            raise ValueError("replace_word requires string 'to'")
        dst = _expand_vars(dst_template, config)

        case_sensitive = bool(rule.get("case_sensitive", False))
        preserve_case = bool(rule.get("preserve_case", True))
        only_in_questions = bool(rule.get("only_in_questions", False))

        flags = 0
        if not case_sensitive:
            flags |= re.IGNORECASE
        pat = re.compile(rf"\b{re.escape(src)}\b", flags=flags)

        def replace_in_segment(seg: str) -> str:
            if preserve_case:
                return pat.sub(lambda m: _apply_leading_case(dst, m.group(0)), seg)
            return pat.sub(dst, seg)

        if not only_in_questions:
            return replace_in_segment

        def replace_questions(text: str) -> str:
            out_parts: list[str] = []
            for s, e, is_q in _iter_sentence_spans(text):
                chunk = text[s:e]
                out_parts.append(replace_in_segment(chunk) if is_q else chunk)
            return "".join(out_parts)

        return replace_questions

    if rtype == "replace_regex":
        pattern = rule.get("pattern")
        dst_template = rule.get("to")
        if not isinstance(pattern, str) or not pattern:
            raise ValueError("replace_regex requires non-empty string 'pattern'")
        if not isinstance(dst_template, str):
            raise ValueError("replace_regex requires string 'to'")

        dst = _expand_vars(dst_template, config)

        flags_val = 0
        flags_list = rule.get("flags", [])
        if flags_list is None:
            flags_list = []
        if not isinstance(flags_list, list) or not all(isinstance(x, str) for x in flags_list):
            raise ValueError("replace_regex 'flags' must be a list of strings")
        for f in flags_list:
            if f == "IGNORECASE":
                flags_val |= re.IGNORECASE
            elif f == "MULTILINE":
                flags_val |= re.MULTILINE
            else:
                raise ValueError(f"Unsupported regex flag: {f}")

        preserve_case = bool(rule.get("preserve_case", False))
        pat = re.compile(pattern, flags=flags_val)

        if preserve_case and "\\" not in dst and "$" not in dst:
            return lambda text: pat.sub(lambda m: _apply_leading_case(dst, m.group(0)), text)
        return lambda text: pat.sub(dst, text)

    if rtype == "append_particle":
        particle = rule.get("particle")
        probability = rule.get("probability")
        positions = rule.get("positions")
        if not isinstance(particle, str) or not particle.strip():
            raise ValueError("append_particle requires non-empty string 'particle'")
        particle = particle.strip()
        if not isinstance(probability, (int, float)):
            raise ValueError("append_particle requires numeric 'probability'")
        prob = float(probability)
        if prob <= 0:
            return lambda text: text
        if positions is None:
            positions = ["end_of_sentence"]
        if not isinstance(positions, list) or not all(isinstance(x, str) for x in positions):
            raise ValueError("append_particle 'positions' must be a list of strings")
        if positions != ["end_of_sentence"]:
            raise ValueError("append_particle currently supports only positions=['end_of_sentence']")

        already_pat = re.compile(
            rf"(?:,\\s*)?{re.escape(particle)}\\s*[.!?]+\\s*$", flags=re.IGNORECASE
        )
        punct_pat = re.compile(r"([.!?]+)(\\s*)$")

        def apply(text: str) -> str:
            if not config.enable_particles:
                return text

            out_parts: list[str] = []
            sent_i = 0
            for s, e, _is_q in _iter_sentence_spans(text):
                chunk = text[s:e]
                sent_i += 1

                # Only operate on real sentences with ending punctuation.
                if not punct_pat.search(chunk) or already_pat.search(chunk):
                    out_parts.append(chunk)
                    continue

                if prob < 1:
                    if config.deterministic:
                        key = f"{config.seed}|{dialect_id}|append_particle|{rule_index}|{sent_i}|{chunk}"
                        if _hash_float_0_1(key) >= prob:
                            out_parts.append(chunk)
                            continue
                    else:
                        # Non-deterministic mode: still seedable.
                        key = f"{config.seed}|{dialect_id}|append_particle|{rule_index}|{sent_i}"
                        if _hash_float_0_1(key) >= prob:
                            out_parts.append(chunk)
                            continue

                m = punct_pat.search(chunk)
                assert m is not None
                chunk = (
                    chunk[: m.start(1)]
                    + f", {particle}"
                    + m.group(1)
                    + m.group(2)
                )
                out_parts.append(chunk)
            return "".join(out_parts)

        return apply

    raise ValueError(f"Unknown rule type: {rtype!r}")


def transform(
    text: str,
    dialect_id: str,
    *,
    deterministic: bool | None = None,
    seed: int | None = None,
    enable_particles: bool | None = None,
    pronoun_subject: str | None = None,
    pronoun_object: str | None = None,
    pronoun_possessive: str | None = None,
    max_passes: int | None = None,
    strict_idempotency: bool | None = None,
) -> str:
    """
    Transform text using a dialect pack.

    Notes:
    - Default config is deterministic and does not add particles.
    - Protected terms are masked and restored verbatim.
    """
    if not isinstance(text, str):
        raise TypeError("text must be str")
    if not isinstance(dialect_id, str) or not dialect_id:
        raise TypeError("dialect_id must be non-empty str")

    base = _default_config()
    config = DialectTransformConfig(
        deterministic=base.deterministic if deterministic is None else bool(deterministic),
        seed=base.seed if seed is None else int(seed),
        enable_particles=base.enable_particles if enable_particles is None else bool(enable_particles),
        pronoun_subject=base.pronoun_subject if pronoun_subject is None else str(pronoun_subject),
        pronoun_object=base.pronoun_object if pronoun_object is None else str(pronoun_object),
        pronoun_possessive=base.pronoun_possessive if pronoun_possessive is None else str(pronoun_possessive),
        max_passes=base.max_passes if max_passes is None else int(max_passes),
        strict_idempotency=base.strict_idempotency if strict_idempotency is None else bool(strict_idempotency),
    )

    resolved = _DEFAULT_REGISTRY.resolve(dialect_id)
    protected_terms = (*GLOBAL_PROTECTED_TERMS, *resolved.protected_terms)
    compiled_rules = [
        _compile_rule(r, config=config, dialect_id=dialect_id, rule_index=i)
        for i, r in enumerate(resolved.rules)
    ]

    def apply_once(src_text: str) -> str:
        masked, mapping = _mask_protected(src_text, protected_terms)
        out = masked
        for fn in compiled_rules:
            out = fn(out)
        out = _unmask(out, mapping)
        return out

    out = text
    seen: set[str] = {out}
    max_iters = max(1, config.max_passes)
    for _ in range(max_iters):
        new = apply_once(out)
        if new == out:
            return out
        if new in seen:
            # Cycle detected; return the last stable-ish output.
            break
        seen.add(new)
        out = new

    if config.strict_idempotency and apply_once(out) != out:
        raise RuntimeError(f"Dialect transform did not converge for {dialect_id}")
    return out
