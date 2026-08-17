# Python Debugging (pdb + debugpy)

Condensed from the former `python-debugpy` skill. Three tools, picked by
situation:

| Tool | When |
|---|---|
| `breakpoint()` + pdb | Local, interactive, simplest |
| `python -m pdb` | Launch a script under pdb with no source edits |
| `debugpy` + `remote-pdb` | Remote, headless, long-lived processes |

## pdb Quick Reference

Inside any `(Pdb)` prompt:

| Command | Action |
|---|---|
| `n` | next line (step over) |
| `s` | step into |
| `r` | return from current function |
| `c` | continue |
| `l` / `ll` | list source / full function |
| `w` | where (stack trace) |
| `u` / `d` | move up / down the stack |
| `a` | print args of current function |
| `p expr` / `pp expr` | print / pretty-print |
| `b file:line` | set breakpoint |
| `interact` | drop into Python REPL (Ctrl+D to exit) |
| `!stmt` | execute arbitrary Python |
| `q` | quit |

## Recipe 1: Local breakpoint

Add `breakpoint()` in the source, run normally. Lands at that line.

```python
def compute(x, y):
    result = some_helper(x)
    breakpoint()
    return result + y
```

**Don't forget to remove before committing.** Add a pre-commit grep:
```bash
rg -n 'breakpoint\\(\\)' --type py
```

## Recipe 2: Launch under pdb (no source edits)

```bash
python -m pdb path/to/script.py arg1 arg2
# Lands at first line. Set breakpoints, then 'c' to continue.
```

## Recipe 3: Debug a pytest test

```bash
# Drop to pdb on failure
python -m pytest tests/path/to/test_file.py::test_name --pdb -p no:xdist

# Show locals without pdb
python -m pytest tests/path/to/test_file.py --showlocals --tb=long
```

Always add `-p no:xdist` — pdb does NOT work under xdist.

## Recipe 4: Post-mortem

```python
import pdb, sys
try:
    run_the_thing()
except Exception:
    pdb.post_mortem(sys.exc_info()[2])
```

## Recipe 5: Remote debug with debugpy

For long-lived processes (gateway, daemon). Install: `pip install debugpy`.

```python
import debugpy
debugpy.listen(("127.0.0.1", 5678))
print("Waiting for debugger...", flush=True)
debugpy.wait_for_client()
debugpy.breakpoint()
```

Or launch with no source edit:
```bash
python -m debugpy --listen 127.0.0.1:5678 --wait-for-client your_script.py
```

### Alternative: remote-pdb (cleaner for terminal agents)

```bash
pip install remote-pdb
```

In code:
```python
from remote_pdb import set_trace
set_trace(host="127.0.0.1", port=4444)
```

Then from terminal: `nc 127.0.0.1 4444` — you get a `(Pdb)` prompt.

## Common Pitfalls

1. **pdb under pytest-xdist silently hangs.** Always use `-p no:xdist`.
2. **`breakpoint()` in CI non-TTY hangs.** Never commit it.
3. **`PYTHONBREAKPOINT=0` disables all breakpoint() calls.** Check the env.
4. **debugpy.listen blocks only with wait_for_client().** Without it, execution continues.
5. **Attach to PID fails on hardened kernels.** `ptrace_scope=1` (Ubuntu default) blocks injection.
6. **asyncio:** pdb works in coroutines but `await` inside pdb requires Python 3.13+. Use `remote-pdb` for async.
7. **Forking:** pdb does not follow forks. Each child needs its own `set_trace()`.
