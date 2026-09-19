# Agent Kit coordination runtime

`agentkit.py` keeps several agents working in one project from stepping on each
other. It is one standard-library Python file. Run it from inside the project
being coordinated, by its path in the installed skill; `--help` lists every
command and `<command> --help` its options. Every command accepts `--as`.

State is a SQLite store owned by the project. In a git repository it lives in
the shared git directory (`<git-common-dir>/agent-kit/state.db`), so every
worktree sees the same tasks and nothing is ever committed. Outside git it lives
in `.agent-kit/state/`; ignore that folder. `AGENTKIT_DB` overrides both. Run it
from inside the repository whose store you mean: a nested or neighbouring
repository has its own store. Never edit the store by hand, and never maintain
task status in Markdown: `status` generates the board.

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
   non-scope, verification, required evidence, danger zones, base, reviewer.
3. Test the scope against the design before editing: read the code the change
   needs. If it needs files outside the scope, stop and ask the lead to `revise`;
   do not widen it yourself.
4. Touch only the declared scope. **Put the task ID in the subject line of every
   commit for it** (`Batch mesh uploads (T001)`): that is how its commits are
   told apart from other agents' in a shared checkout.
5. `heartbeat --as ann` renews your lease (default 30 minutes; `--lease`). A
   lease that lapses returns the task to the queue. Exit code 3 means the lead
   revised the spec: `show` it, reconcile, then `ack T001`.
6. `progress T001 -m "..."` records checkpoints. If you cannot continue,
   `block T001 --reason "..." --retry-when "..."`; you keep the scope.
7. `done T001 --evidence tests="<command>: exit 0" --evidence commit=<sha>`
   submits for review. Required evidence keys are enforced. The task's files,
   commits, and anything outside its scope are recorded (see Checking changes).
   `--gap` names what is still missing.
8. `next` again.

After a timeout or crash, inspect before retrying: `show T001`. Claiming a task
you already hold is a safe no-op; submitting twice is refused, not duplicated.

## Checking changes

A task's changes are the commits since its claim whose subject names it, any
commit given as `--evidence commit=`, and uncommitted files inside its scope.
`check T001` and `done` report:

- files the task's own commits changed outside its scope (exit 1 for `check`);
- uncommitted changes that **no** open task claims: somebody edited without a
  claim (exit 1 for `check`);
- uncommitted changes inside another open task's scope, labelled with that task:
  in a shared checkout that is the other agent's work, not a finding.

Separate worktrees per agent are the cleanest arrangement. When the project
forces one shared checkout (for example, a tool that loads it from one path),
commit your task's work promptly with the task ID in the subject.

In a shared checkout, anything you run measures every task's working state at
once: another task's uncommitted tests are counted in your suite, and its fix
or breakage can change your result. Gather evidence on a clean worktree at your
commit, then remove it:

```text
git worktree add --detach <scratch-dir> <sha>
(cd <scratch-dir> && <test command>)
git worktree remove <scratch-dir>
```

Put `<scratch-dir>` outside the checkout, for example in the system temp folder.

`done` warns when other tasks' uncommitted files were present and records them
beside the evidence as `uncommitted_other_tasks`.

## Reviews and notes

- `review T001 --as bob --verdict accept|reject -m "what I checked"` records a
  verdict on work in review. The agent who did the work cannot review it. If the
  task names a reviewer, only that reviewer can.
- `note T001 --as anyone -m "..."` attaches a note to any open task, claimed or
  not. It is how a lead records a finding on a ready task, or a worker asks for
  review after `done`.

## Short holds on shared resources

Some things are exclusive for minutes, not for a whole task: a running editor
that must close for a build, a dev server, a database being reset.

```text
agentkit.py hold ue-editor --as ann --for 10 --reason "rebuilding binaries"
agentkit.py unhold ue-editor --as ann
```

A hold is refused while another agent holds the resource or an open task has it
in scope. It expires on its own, blocks claims of tasks that list the resource,
and shows on the board. Release it as soon as you are done.

## Lead

- `add --as lead --title ... --goal ... --path 'src/render/**' --resource db-schema
  --after T001 --need code_edit --base main --non-scope ... --verify ... --evidence
  tests,commit --danger ... --reviewer bob --priority 10` creates a ready task.
  `--source` records where it came from; `--proposed` records it without
  releasing it.
- **Priority: higher runs first** (default 0). The board lists ready work in the
  order `next` offers it.
- Draw a scope from a sketch of the change, not from the file list alone. Prefer
  literal paths for files known in advance. Two globs overlap unless their literal
  parts show no file could match both (`authoring*.py` and `basic*.py` do not
  overlap; `*.py` and `x*.py` do; anything undecidable counts as overlapping).
- A worker's `add` is only a proposal. `approve` releases it. Discovery is not
  permission.
- `revise` changes a spec; a material change bumps its revision and the holder
  must acknowledge it. `--priority` and `--reviewer` change without a new
  revision.
- `accept` (or `accept --merged`), `reject --reason`, `unblock`, `release`,
  `close --merged | --reason`, `reclaim`. You cannot accept work you did. When
  the task names a reviewer, `accept` needs that reviewer's accepting verdict on
  the current attempt, or `--override-review "<why>"`, which is recorded.
- `status [--write BOARD.md]`, `workers`, `log [task]`.

## What it enforces

- A task cannot be claimed while any open task holds an overlapping path or the
  same named resource, or while another agent has a short hold on one of its
  resources. Scope is held from claim until close, including review.
- Dependencies must be accepted or closed first; required capabilities must match.
- A claim must start from the task's `--base` when the project is a git checkout.
- An older runtime refuses a store a newer one has upgraded; update every agent's
  installed copy together.
- Every change is an event in an append-only history.
