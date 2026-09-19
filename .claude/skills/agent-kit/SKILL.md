---
name: agent-kit
description: >-
  Use when several AI agents or sessions work in the same project and must not
  step on each other: acting as lead or worker, creating and claiming bounded
  tasks, holding file and resource scopes, reporting blocks and evidence,
  reviewing or reworking results, and asking for the next task. Do not use it for
  PASS source extraction or for changing the agent-kit cards themselves.
---

# Agent Kit

Coordinate through the Agent Kit runtime, never through hand-kept status files.
Run it from the project being coordinated:

```bash
python library/agent-kit/coordination/runtime/agentkit.py --help
```

Read `library/agent-kit/coordination/runtime/README.md` for the lead and worker
loops before the first coordinated action. Retrieve cards only for the decision
at hand:

```bash
python PASS/tools/find_relevant.py --package metaskills --cues "<task cues>" --limit 5
python PASS/tools/find_relevant.py --package agent-kit --cues "<task cues>" --limit 8
```

Use the PASS-authoring skill instead when studying a source or changing cards,
modules, schema, or releases.
