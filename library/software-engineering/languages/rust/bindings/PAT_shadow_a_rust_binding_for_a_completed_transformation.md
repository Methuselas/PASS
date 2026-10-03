---
object_id: PAT_shadow_a_rust_binding_for_a_completed_transformation
object_type: pattern
name: Shadow a Rust Binding for a Completed Transformation
library_path: [software-engineering, languages, rust, bindings]
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, bindings, shadowing, transformation, types]
cross_links:
- rel: related_to
  target_object_id: PAT_minimize_variable_span_and_live_time
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: medium
references: []
variants: []
---

# Shadow a Rust Binding for a Completed Transformation

## Pattern Rule
**IF** a Rust value moves through a completed representation change but keeps the same role in the surrounding code
**THEN** shadow the binding with a new `let` so the transformed value may have a new type and remains immutable afterward
**ELSE** use distinct names when both representations remain meaningful or must be used together.

## Do
- Use the initializer of the new binding to consume or borrow the previous one, such as trimming and parsing textual input into a number.
- Shadow at the point where the old representation stops being valid for subsequent work.
- Let the new type make stale operations on the old representation unavailable after the transformation.
- Prefer distinct names when an error message, audit record, or later decision still needs the original form.

## Don't
- Don't use `mut` to model a type-changing transformation; reassignment preserves the binding's type.
- Don't shadow across a long distance where a reader cannot see which declaration a use resolves to.
- Don't reuse a name merely to avoid naming two genuinely different concepts.

## Checklist
- Does the value keep one conceptual role before and after the transformation?
- Is the old representation intentionally unavailable after the new `let`?
- Would any later step need both forms at once?
- Is the shadowing declaration close enough that resolution is obvious?

## Notes
Shadowing creates a new binding; mutation changes the value behind an existing typed binding. That distinction makes shadowing suitable for phase changes such as raw text becoming validated numeric input while preserving the concise domain name used by later code.

