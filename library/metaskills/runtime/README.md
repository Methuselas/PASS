# AP runner

`ap_runner.py` steps an Action Protocol (AP) card one step at a time. The card
stays the only source of the method; the runner only reads it and owns the
order. It is one standard-library Python file. Run it from the project you are
working in, by its path in the installed skill; `--help` lists every command.

## When to use it

Execute every AP through the runner. Do not work from the AP card directly, and
do not read ahead: the runner shows the current step plus the full text of every
Pattern that step names, which is the retrieval that step needs.

```text
ap_runner.py start --ap <AP_id> --task "<one line naming the task>"
ap_runner.py current                       # the current step, again
ap_runner.py done --step N --did "<what you actually did>" [--artifact <path>]
ap_runner.py gate --step N --verdict pass|fail --reason "<evidence>"
ap_runner.py skip --step N --reason "<why this step does not apply>"
ap_runner.py back --to M --reason "<what the gate or discovery showed>"
ap_runner.py status [--all]
ap_runner.py record                        # completion record, JSON
ap_runner.py abandon --run <id> --reason "<the user's instruction>"
```

## Rules it enforces

- Only the current step can be accounted for; a later step is refused.
- `done` needs a non-empty statement of what was done. Name produced files with
  `--artifact`; the runner records their hashes.
- A gate step (its title names a gate, or it contains a `Gate.` check) needs
  `gate --verdict`. A failed gate stays current: revise, or `back` to the step
  that must change, then judge it again. A gate can never be skipped.
- Any other step may be skipped only with a reason, and the completion record
  lists every skip.
- A step that names another AP expects that AP to be run with its own `start`
  and finished first.
- If the AP card changes during a run, the run stops; start a new one.

The runner cannot see the work. A record says what you report, so report only
what you did. An honest skip is fine; an invented `done` is not.

## State

Runs are JSON files owned by the project. In a git repository they live in the
shared git directory (`<git-common-dir>/skillforge/ap-runs/`), so every worktree
sees them and nothing is committed; otherwise in `.skillforge/ap-runs/` (ignore
that folder). `SKILLFORGE_AP_STATE` overrides both. Never edit a run file by
hand; `status` and `record` read it for you. A run survives a lost conversation:
`current` resumes exactly where it stopped.
