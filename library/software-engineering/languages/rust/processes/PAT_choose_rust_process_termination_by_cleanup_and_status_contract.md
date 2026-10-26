---
object_id: PAT_choose_rust_process_termination_by_cleanup_and_status_contract
object_type: pattern
name: Choose Rust Process Termination by Cleanup and Status Contract
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
- process
- exit
- exitcode
- panic
- abort
- cleanup
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

# Choose Rust Process Termination by Cleanup and Status Contract

## Pattern Rule
**IF** Rust code must turn an outcome into process termination
**THEN** prefer normal return from `main` through `Result` or `ExitCode` when cleanup should run, use `process::exit` only for immediate status-bearing termination that may skip Rust destructors, and reserve panic or `process::abort` for their distinct failure semantics
**ELSE** keep the failure as `Result` until an outer layer actually owns process-level policy

## Do
- Return `Result` or `ExitCode` from `main` for ordinary CLI success and failure so local values can leave scope normally before the process reports its status.
- Use `process::exit(code)` only when immediate process-wide termination is intentional and code has already settled any cleanup that depends on Rust `Drop` or buffered writers.
- Treat panic as a broken invariant or other unrecoverable program condition, and remember that destructor unwinding occurs only with an unwinding panic strategy.
- Use `process::abort` for abnormal immediate termination where running ordinary Rust cleanup is specifically not part of the contract.

## Don't
- Don't use `process::exit` in the middle of reusable logic just to avoid returning an error; it skips Rust destructors on active stacks.
- Don't choose `panic!` because you need cleanup; `panic = "abort"` terminates without unwinding.
- Don't describe `abort` as a portable application exit-code mechanism; its abnormal termination details are platform-specific.

## Checklist
- Can the outcome be returned normally from `main` as `Result` or `ExitCode`?
- Which destructors, buffered writes, or other scoped cleanup must complete before termination?
- Is a panic signaling a program invariant failure rather than an environmental or user error?
- Does any assumption about panic cleanup remain correct under the configured panic strategy?

## Notes
`process::exit` and `process::abort` terminate without Rust stack unwinding, so active Rust destructors are not run. Panics have configurable strategy: an unwinding panic runs destructors while unwinding the affected thread, whereas an aborting panic does not. Normal `main` return through a type implementing `Termination`, such as `Result` or `ExitCode`, is therefore the clean default when a program simply needs to report success or failure to its parent.
