---
object_id: PAT_choose_rust_child_stdio_by_parent_child_contract
object_type: pattern
name: Choose Rust Child Stdio by the Parent-Child Contract
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
- stdio
- pipes
- ipc
- command
cross_links: []
reference:
  source_title: Practical System Programming for Rust Developers
  author: Prabhu Eshwarla
confidence: medium
references: []
variants: []
---

# Choose Rust Child Stdio by the Parent-Child Contract

## Pattern Rule
**IF** a Rust parent process must control where a child reads input or sends output and diagnostics
**THEN** configure each child standard stream from the parent-child communication contract before launch, and retain only the pipe endpoints the parent must actively use

## Do
- Leave a stream inherited when direct terminal or parent-stream behavior is the intended contract; `spawn` and `status` inherit standard streams by default.
- Use `Stdio::piped()` for stdin, stdout, or stderr only when the parent must programmatically write or read that stream.
- When using `output`, remember that stdout and stderr are captured by default while child stdin is closed rather than interactively inherited.
- Drop any separately retained child-stdin writer when no more data will be sent so a child protocol that waits for end-of-file can make progress.
- If a child can emit substantial data on more than one captured stream, choose a collection strategy that drains the required streams without allowing one full pipe to deadlock the other side.

## Don't
- Do not pipe every stream by default when the parent does not need to consume or produce it.
- Do not wait for a child that is waiting for end-of-file while the parent still holds an open write endpoint that keeps that input stream alive.
- Do not assume captured stdout and stderr are merely presentation details; they are bounded communication channels with blocking behavior.

## Checklist
- Which process should own each standard stream after launch?
- Which streams need programmatic capture rather than inheritance?
- What event closes every parent-held write endpoint and lets the child observe end-of-file?
- Can either side block because the other side is not draining or closing a pipe?

## Notes
Child stdio is part of the process protocol, not incidental plumbing. Rust lets the parent decide inheritance, null routing, and pipes at the `Command` boundary; the correct choice follows from who must exchange bytes with whom and how completion is detected.
