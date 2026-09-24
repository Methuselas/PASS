---
object_id: PAT_stream_unreal_editor_batch_processes_with_bounded_feedback
object_type: pattern
name: Stream Unreal Editor Batch Processes with Bounded Feedback
library_path:
- software-engineering
- unreal-engine
- editor
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: PAT_prefer_explicit_error_signaling_for_recoverable_errors
tags:
- unreal_engine
- editor_tools
- processes
- progress
- cancellation
cross_links:
- rel: related_to
  target_object_id: PAT_report_unreal_tool_outcomes_through_a_small_facade
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Stream Unreal Editor Batch Processes with Bounded Feedback

## Pattern Rule
**IF** an Unreal editor action launches a commandlet or other long-running child process
**THEN** give the process an explicit lifetime owner, stream its output through a stable progress/result protocol, expose cancellation, and finish with a machine-readable outcome plus navigable editor diagnostics.

## Do
- Build the executable and argument list from validated paths and quote values that may contain spaces. Treat process creation, pipe creation and launch as separate fallible steps.
- Retain the process and pipe handles in one owner. Close every acquired handle on launch failure, completion, cancellation and module shutdown.
- Keep the editor responsive while collecting output. Drain complete lines incrementally, preserve an incomplete tail between reads and consume the final pipe contents after the process stops.
- Prefer stable machine-oriented progress markers or structured output. When the total is not yet known, show indeterminate work instead of manufacturing a percentage; guard zero-item totals.
- Make cancellation idempotent: request termination once, continue cleanup and report `cancelled` distinctly from `failed` and `succeeded`.
- Check the child exit code and captured diagnostics. Do not infer success merely because no recognized error string appeared.
- Normalize and deduplicate diagnostics by a stable key. Turn a path into an `FAssetNameToken` only after it resolves to an expected project asset; keep the diagnostic text when it does not.
- Create a fresh message-log page per run and publish an explicit summary, including a successful empty result, so users never have to infer whether the action ran.

## Don't
- Don't sleep in a tight editor-thread polling loop for work that can be ticked or completed asynchronously.
- Don't make correctness depend on prose log wording owned by another engine version when a versioned marker or result format can be provided.
- Don't kill a process and abandon its pipes, task UI or retained callbacks.
- Don't open arbitrary paths parsed from untrusted process output as clickable assets.

## Checklist
- Can launch failure, cancellation, nonzero exit and success be distinguished?
- Does the editor remain usable and does progress stay bounded when output arrives in partial or repeated chunks?
- Are process, pipe, callback and UI resources released on every exit path?
- Do diagnostics link only to validated assets while retaining useful text for everything else?

## Notes
The process boundary is both a responsiveness boundary and a trust boundary. A slow-task dialog is presentation, not lifetime management; an empty message page is feedback, not proof of success unless the exit result agrees.
