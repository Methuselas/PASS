# Agent Kit coordination runtime

`agentkit.py` keeps several agents working in one project from stepping on each
other. It is one standard-library Python file. Run it from inside the project
being coordinated, by its path in the installed skill; `--help` lists every
command and `<command> --help` its options.

State is a SQLite store owned by the project. In a git repository it lives in
the shared git directory (`<git-common-dir>/agent-kit/state.db`), so every
worktree sees the same tasks and nothing is ever committed. Outside git it lives
in `.agent-kit/state/`; ignore that folder. `AGENTKIT_DB` overrides both. Never
edit the store by hand, and never maintain task status in Markdown: `status`
generates the board.

## Every agent

Name yourself on every call with `--as <name>` (or `AGENTKIT_AS`). Register once,
honestly: only capabilities you can actually exercise.

```text
agentkit.py register ann --role worker --cap code_edit,tests,git
agentkit.py register lead --role lead
```

Registering again later is how you resume: it lists what you still hold.

## Worker loop

1. `next --as ann` shows the task you may take, or why nothing is eligible.
   `next --claim` takes it. The claim is atomic: if it fails, someone else won.
2. Read the whole spec (`show T001`): goal, paths and resources you own,
   non-scope, verification, required evidence, danger zones, base.
3. Touch only the declared scope. `check T001` exits 1 if this checkout has
   changes outside it.
4. `heartbeat --as ann` renews your lease (default 30 minutes; `--lease`). A
   lease that lapses returns the task to the queue. Exit code 3 means the lead
   revised the spec: `show` it, reconcile, then `ack T001`.
5. `progress T001 -m "..."` records checkpoints. If you cannot continue,
   `block T001 --reason "..." --retry-when "..."`; you keep the scope.
6. `done T001 --evidence tests="<command>: exit 0" --evidence commit=<sha>`
   submits for review. Required evidence keys are enforced; changed files and any
   out-of-scope files are recorded. `--gap` names what is still missing.
7. `next` again.

After a timeout or crash, inspect before retrying: `show T001`. Claiming a task
you already hold is a safe no-op; submitting twice is refused, not duplicated.

## Lead

- `add --as lead --title ... --goal ... --path 'src/render/**' --resource db-schema
  --after T001 --need code_edit --base main --non-scope ... --verify ... --evidence
  tests,commit --danger ...` creates a ready task. `--source` records where it came
  from; `--proposed` records it without releasing it.
- A worker's `add` is only a proposal. `approve` releases it. Discovery is not
  permission.
- `revise` changes a spec; a material change bumps its revision and the holder
  must acknowledge it. `--priority` reorders without a new revision.
- `accept` (or `accept --merged`), `reject --reason`, `unblock`, `release`,
  `close --merged | --reason`, `reclaim`.
- `status [--write BOARD.md]`, `workers`, `log [task]`.

## What it enforces

- A task cannot be claimed while any open task holds an overlapping path glob or
  the same named resource. Scope is held from claim until close, including review.
- Dependencies must be accepted or closed first; required capabilities must match.
- A claim must start from the task's `--base` when the project is a git checkout.
- Every change is an event in an append-only history.
