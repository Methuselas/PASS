---
object_id: PAT_choose_rust_child_process_api_by_completion_contract
object_type: pattern
name: Choose the Rust Child-Process API by the Completion Contract
library_path:
- software-engineering
- languages
- rust
- processes
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- rust
- processes
- command
- child-process
- stdio
- exit-status
cross_links:
- rel: related_to
  target_object_id: PAT_keep_rust_failures_as_result_until_recovery_context_exists
reference:
  source_title: Practical System Programming for Rust Developers
  author: Prabhu Eshwarla
confidence: medium
references: []
variants: []
---

# Choose the Rust Child-Process API by the Completion Contract

## Pattern Rule
**IF** a Rust program launches an external program and the caller must choose whether it needs a live child, only completion status, or captured output
**THEN** choose spawn, status, or output to match that completion contract, and explicitly finish the lifecycle of any Child handle retained by the parent

## Do
- Use `spawn` when the parent must retain a `Child` handle for streaming I/O, polling, waiting, or termination; keep ownership of that lifecycle until the child has been observed and reaped with `wait`, `try_wait`, or `wait_with_output` as appropriate.
- Use `status` when the parent only needs to wait for completion and inspect the exit status while standard streams follow the configured status/spawn policy.
- Use `output` when the parent should wait for completion and collect stdout and stderr as data; account for its non-interactive stdin behavior.
- Treat failure to start the child and an unsuccessful exit after a successful start as separate outcomes.

## Don't
- Do not treat a successful `spawn`, `status`, or `output` call as proof that the child command itself succeeded; inspect the returned `ExitStatus`.
- Do not drop a `Child` handle assuming Rust will kill or wait for the process; `Child` has no automatic wait-on-drop contract, and unreaped exited children can consume operating-system resources on some platforms.
- Do not choose a blocking completion API when the parent still needs to interact with the running child.

## Checklist
- Does the parent need a live handle after launch, only the exit status, or captured output?
- Who waits for or otherwise reaps a child created with `spawn`?
- Are spawn errors distinguished from nonzero or signal-based child termination?
- Does the chosen API give stdin/stdout/stderr the interaction behavior the child actually needs?

## Notes
Rust process APIs encode different lifecycle contracts. `spawn` returns a live `Child` and therefore transfers lifecycle responsibility to the parent; `status` and `output` combine launch with waiting. The narrowest API that matches the required interaction keeps waiting, reaping, status inspection, and output collection explicit.
