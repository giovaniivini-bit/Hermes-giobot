# Node.js Inspect Debugger

Condensed from the former `node-inspect-debugger` skill.

Two tools:
- **`node inspect`** — built-in CLI REPL, zero install
- **`chrome-remote-interface`** — scriptable CDP automation

## `node inspect` REPL

Launch paused on first line:

```bash
node inspect path/to/script.js
node --inspect-brk $(which tsx) path/to/script.ts   # TypeScript via tsx
```

The `debug>` prompt:

| Command | Action |
|---|---|
| `c` / `cont` | continue |
| `n` / `next` | step over |
| `s` / `step` | step into |
| `o` / `out` | step out |
| `pause` | pause running code |
| `sb('file.js', 42)` | set breakpoint at line 42 |
| `sb('fnName')` | break on function entry |
| `cb('file.js', 42)` | clear breakpoint |
| `bt` | backtrace |
| `list(5)` | show 5 lines of source |
| `repl` | drop into REPL in current scope |
| `exec expr` | evaluate expression once |
| `restart` | restart script |
| `.exit` | quit |

## Attaching to a Running Process

```bash
# 1. Enable inspector on an existing process
kill -SIGUSR1 <pid>

# 2. Attach
node inspect -p <pid>
# or by WS URL
node inspect ws://127.0.0.1:9229/<uuid>
```

## Programmatic CDP

Install: `npm i -g chrome-remote-interface`

```javascript
const CDP = require('chrome-remote-interface');

(async () => {
  const client = await CDP({ port: 9229 });
  const { Debugger, Runtime } = client;

  Debugger.paused(async ({ callFrames, reason }) => {
    const top = callFrames[0];
    console.log(`PAUSED @ ${top.url}:${top.location.lineNumber + 1}`);

    // Walk scopes
    for (const scope of top.scopeChain) {
      if (scope.type === 'local' || scope.type === 'closure') {
        const { result } = await Runtime.getProperties({
          objectId: scope.object.objectId,
        });
        for (const p of result)
          console.log(`  ${scope.type}.${p.name} =`, p.value);
      }
    }
    await Debugger.resume();
  });

  await Debugger.enable();
  await Debugger.setBreakpointByUrl({ urlRegex: '.*app\\.tsx$', lineNumber: 119 });
  await Runtime.runIfWaitingForDebugger();
})();
```

## Heap Snapshots & CPU Profiles

Swap Debugger for HeapProfiler/Profiler in the CDP driver:

```javascript
// CPU profile for 5 seconds
await client.Profiler.start();
await new Promise(r => setTimeout(r, 5000));
const { profile } = await client.Profiler.stop();
require('fs').writeFileSync('/tmp/cpu.cpuprofile', JSON.stringify(profile));
```

## Common Pitfalls

1. **Wrong line numbers in TS source.** Breakpoints hit the emitted JS. Use `node --enable-source-maps`.
2. **`--inspect` vs `--inspect-brk`.** Use `--inspect-brk` when you need to set breakpoints before any code runs.
3. **Port collisions.** Default is 9229. Use `--inspect=0` for random port.
4. **Child processes.** `NODE_OPTIONS='--inspect-brk'` propagates to every child; each needs a unique port.
5. **Security.** `--inspect=0.0.0.0:9229` exposes arbitrary code execution. Bind to 127.0.0.1.
