# Pack schema (JSON)

Each pack is a JSON file under `dialects/packs/` and must match this shape:

```json
{
  "id": "vlaams/antwerps",
  "label": "Antwerps",
  "inherits": ["vlaams/basis"],
  "notes": "Optional human notes / TODO",
  "protected_terms": ["verplicht", "verboden", "tenzij", "boete", "straf"],
  "rules": [
    {"type": "replace_word", "from": "even", "to": "efkes"},
    {"type": "replace_regex", "pattern": "\\\\bdat is\\\\b", "to": "da’s", "flags": ["IGNORECASE"]},
    {"type": "append_particle", "particle": "zeg", "probability": 0.08, "positions": ["end_of_sentence"]}
  ]
}
```

## Fields

- `id` (string, required): stable pack id, e.g. `vlaams/basis`
- `label` (string, required): human label for listings
- `inherits` (list[string], optional): base packs in order (defaults to `[]`)
- `notes` (string, optional): free text; ignored by the transformer
- `protected_terms` (list[string], required): terms/phrases that must remain unchanged
- `rules` (list[object], required): ordered transformation rules

## `dialects/index.json`

The registry file `dialects/index.json` is a list of entries:

```json
[
  {"id": "vlaams/basis", "label": "Vlaams basis (NL-BE informeel)", "inherits": ["nl/standard"], "file": "vlaams__basis.json"}
]
```

## Replacement variables

Some packs can use variables in `to`, written as `{var}`.

Built-in variables:

- `{pronoun_subject}`: default `"ge"` (configurable)
- `{pronoun_object}`: default `"u"` (configurable)
- `{pronoun_possessive}`: default `"uw"` (configurable)

## Rule types

### `replace_word`

Replace a whole word safely.

Required:
- `from` (string)
- `to` (string)

Optional:
- `case_sensitive` (bool, default `false`)
- `preserve_case` (bool, default `true`)
- `only_in_questions` (bool, default `false`) — only apply inside `?` sentences

### `replace_regex`

Regex replacement (use sparingly).

Required:
- `pattern` (string) — Python `re` pattern
- `to` (string)

Optional:
- `flags` (list[string]) — subset of: `IGNORECASE`, `MULTILINE`
- `preserve_case` (bool, default `false`) — only for simple replacements (no backrefs)

Safeguards:
- Avoid patterns that can match across sentence boundaries (`.*`, DOTALL, etc.).

### `append_particle`

Optionally append a discourse particle (deterministic; default feature is off).

Required:
- `particle` (string)
- `probability` (float 0..1)
- `positions` (list[string]) — currently supports `["end_of_sentence"]`

Notes:
- This rule is ignored unless particles are enabled in transformer config.
- Idempotent: the transformer avoids appending the same particle twice.
