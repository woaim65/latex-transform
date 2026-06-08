# latex-transform

Hermes plugin that intercepts LaTeX math formulas in LLM responses and converts them to Unicode symbols for better display.

## Features

- Converts inline math `$...$` and display math `$$...$$` to Unicode
- Supports Greek letters, math operators, arrows, set theory symbols
- Converts fractions `\frac{a}{b}` to `a/b`
- Handles superscripts/subscripts
- Escaped characters like `\%` → `%`

## Examples

| LaTeX | Unicode |
|-------|---------|
| `$\alpha$` | α |
| `$\frac{1}{2}$` | 1/2 |
| `$x^2$` | x² |
| `$\sum_{i=1}^n$` | ∑ᵢ₌₁ⁿ |
| `$\sqrt{x}$` | √x |

## Installation

Copy to `~/.hermes/plugins/`:

```bash
cp -r latex-transform ~/.hermes/plugins/
```

Add to `config.yaml`:

```yaml
plugins:
  enabled:
    - latex-transform
```

Restart Hermes.
