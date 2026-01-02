# Dialect Language Packs

Dialect packs are **deterministic, rule-based post-processors** that transform a neutral Dutch text into:

- **`vlaams/basis`**: readable NL-BE informal ("Vlaams basis")
- Optionally a **dialect skin** (West-Vlaams, Antwerps, …)

This is **not** LLM translation. Packs may only change **surface form** (spelling, contractions, discourse particles, very common synonyms) and must avoid meaning drift (especially legal meaning).

## Safety: protected terms

Transformer behavior:

- A **global protected list** is always applied (implemented in `src/vlaamscodex/dialects/transformer.py`).
- Each pack also defines `protected_terms`.
- Protected spans are **masked before applying rules**, then restored verbatim.

Packs must never alter legal meaning. In particular, do not change modality/conditions such as:
`verplicht`, `verboden`, `mag`, `moet`, `kan`, `tenzij`, `enkel`, `alleen`, `behalve`, `uitzondering`, `boete`, `straf`.

## Files

- `dialects/index.json`: pack registry (ids/labels/inherits/files)
- `dialects/packs/*.json`: the actual packs
- `dialects/schema.md`: pack format and rule types

## Tooling

- Generate/scaffold packs and update the index:
  - `python tools/generate_dialect_packs.py`
- Validate packs:
  - `python tools/validate_dialect_packs.py`

