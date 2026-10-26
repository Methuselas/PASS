---
object_id: PAT_choose_terminal_input_mode_by_editing_ownership
object_type: pattern
name: Choose Terminal Input Mode by Editing Ownership
library_path:
- software-engineering
- languages
- rust
- io
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- rust
- terminal
- tui
- raw-mode
- canonical-mode
- input
cross_links:
- rel: related_to
  target_object_id: PAT_end_a_rust_resource_guard_with_scope_or_drop
reference:
  source_title: Practical System Programming for Rust Developers
  author: Prabhu Eshwarla
confidence: medium
references: []
variants: []
---

# Choose Terminal Input Mode by Editing Ownership

## Pattern Rule
**IF** a Rust terminal program must decide whether input arrives as completed lines or immediate key events
**THEN** keep canonical line input when the terminal should buffer until line submission, and enter raw/noncanonical input only when the application intentionally owns per-key interaction
**ELSE** leave terminal state unchanged rather than taking responsibility for interaction behavior the program does not need

## Do
- Use line-oriented input for commands, prompts, and parsers that do not need to react before the user submits a line.
- Enter raw or noncanonical mode only around the interactive region that needs immediate keypresses, such as cursor movement or a text-viewer event loop.
- Treat terminal mode as scoped mutable state and restore the previous mode on normal return, error paths, and unwinding where the terminal library supports guard-based restoration.
- Flush rendered terminal output at the boundary where the next input event assumes that frame is visible.

## Don't
- Don't switch a line-oriented CLI into raw mode merely to read stdin; doing so transfers editing and echo responsibilities to the application without a need.
- Don't assume one raw-mode API is portable across every terminal backend or target platform.
- Don't leave the caller's terminal in a modified mode after the interactive portion exits.

## Checklist
- Does this interaction need individual key events before line submission?
- Which layer owns editing, echo, cursor behavior, and key interpretation while raw mode is active?
- Is previous terminal state restored on every exit path the chosen library can cover?
- Is output flushed before the next event depends on the newly rendered state?

## Notes
Canonical and raw/noncanonical modes divide responsibility. Canonical input lets the terminal line discipline collect input until line submission; raw-style interaction exposes input immediately so the application can interpret keys itself. Entering raw mode is therefore a resource-state transition, not merely an input-method preference, and its lifetime should be as narrow and recoverable as possible.
