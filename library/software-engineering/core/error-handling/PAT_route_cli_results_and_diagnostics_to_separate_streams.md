---
object_id: PAT_route_cli_results_and_diagnostics_to_separate_streams
object_type: pattern
name: Route CLI Results and Diagnostics to Separate Streams
library_path: [software-engineering, core, error-handling]
stage_binding: 0 design
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags: [cli, stdout, stderr, diagnostics, composition]
cross_links:
- rel: related_to
  target_object_id: PAT_dont_hide_errors
- rel: related_to
  target_object_id: PAT_match_failure_to_scope_of_recoverability
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
references: []
variants: []
---

# Route CLI Results and Diagnostics to Separate Streams

## Pattern Rule
**IF** a command-line program emits both requested results and messages about failures or execution state
**THEN** reserve standard output for the primary result and send diagnostics to standard error, with a nonzero exit status when the requested operation fails.

## Do
- Treat standard output as the program's composable data channel: it should remain safe to redirect to a file or pipe into another command.
- Send usage errors, failed-operation context, warnings, and debugging diagnostics to standard error so they remain visible when results are redirected.
- Return zero only when the command fulfilled its contract, and use a documented nonzero status for failure.
- Test the channels independently by capturing or redirecting them and asserting both content and exit status.

## Don't
- Don't mix a successful result with error prose on standard output; downstream consumers cannot reliably separate them.
- Don't report a failed operation while returning a success status.
- Don't treat the terminal display as the interface contract; redirection and pipelines are ordinary callers too.
- Don't make incidental progress text part of a machine-consumable result unless the output format explicitly includes it.

## Checklist
- If standard output is redirected, do diagnostics remain observable?
- If standard error is redirected, does standard output contain only the promised result format?
- Does every failure path produce a nonzero exit status?
- Are channel behavior and status verified at the process boundary?

## Notes
The two streams let one process serve both people and other programs without corrupting either interface. A terminal often renders them together, which can hide accidental mixing; separate capture exposes the actual contract. Exit status is the third part of that contract because callers should not have to parse diagnostic prose to decide whether the operation succeeded.

