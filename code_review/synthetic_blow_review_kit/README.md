# Synthetic Blow Review Kit

Files:

- `synthetic_blow.md` — the Codex-ready review spec/prompt.
- `source_notes.md` — sources, caveats, and extraction notes.

Recommended use:

```text
Use synthetic_blow.md as your code review spec. Review this repository/diff through that lens. Do not impersonate Jonathan Blow; use the public-principles-based reviewer described in the file. Follow the output format exactly.
```

The kit is designed for a Python/RL project, with extra attention to Gymnasium/Farama semantics, PyTorch reproducibility/performance, replay buffers, tensor data flow, config complexity, and experiment correctness.
