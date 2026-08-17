# Codebase Inspection with pygount

Condensed from the former `codebase-inspection` skill.

Analyze repositories for lines of code, language breakdown, file counts, and
code-vs-comment ratios using `pygount`.

## Prerequisites

```bash
pip install pygount
```

## Basic Summary

```bash
cd /path/to/repo
pygount --format=summary \
  --folders-to-skip=".git,node_modules,venv,.venv,__pycache__,.cache,dist,build,.next,.tox,.eggs,*.egg-info" \
  .
```

## Common Folder Exclusions

| Project Type | Folders to Skip |
|---|---|
| Python | `.git,venv,.venv,__pycache__,.cache,dist,build,.tox,.eggs,.mypy_cache` |
| JS/TS | `.git,node_modules,dist,build,.next,.cache,.turbo,coverage` |
| General | `.git,node_modules,venv,.venv,__pycache__,.cache,dist,build,.next,.tox,vendor,third_party` |

## Filter by Language

```bash
# Only Python files
pygount --suffix=py --format=summary .

# Python and YAML
pygount --suffix=py,yaml,yml --format=summary .
```

## Output Formats

```bash
# Summary table (recommended)
pygount --format=summary .

# JSON for programmatic use
pygount --format=json .
```

## Interpreting Results

| Column | Meaning |
|---|---|
| Language | Detected programming language |
| Files | Number of files |
| Code | Lines of actual code |
| Comment | Lines that are comments |
| % | Percentage of total |

Special pseudo-languages: `__empty__`, `__binary__`, `__generated__`, `__duplicate__`, `__unknown__`

## Pitfalls

1. **Always exclude .git, node_modules, venv** — without `--folders-to-skip`,
   pygount crawls everything and may hang on large dependency trees.
2. **Markdown shows 0 code lines** — pygount classifies all Markdown as comments.
3. **Large monorepos** — use `--suffix` to target specific languages.
