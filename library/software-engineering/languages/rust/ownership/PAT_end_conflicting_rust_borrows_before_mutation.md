---
object_id: PAT_end_conflicting_rust_borrows_before_mutation
object_type: pattern
name: End Conflicting Rust Borrows Before Mutation
library_path: [software-engineering, languages, rust, ownership]
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, borrowing, mutable_references, aliasing, lifetimes]
cross_links:
- rel: related_to
  target_object_id: PAT_minimize_variable_span_and_live_time
- rel: related_to
  target_object_id: PAT_default_rust_bindings_to_immutable
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: medium
references: []
variants: []
---

# End Conflicting Rust Borrows Before Mutation

## Pattern Rule
**IF** a Rust mutation conflicts with an active shared borrow or another mutable borrow
**THEN** place the borrow's last use before the mutation and keep the borrowed result's live range as short as the operation requires
**ELSE** preserve the shared borrows when the phase is read-only or the single mutable borrow when it is an exclusive update phase.

## Do
- Group all uses of a derived reference before the operation that needs mutable access to its source.
- Let non-lexical lifetime analysis end a borrow after its last use; introduce an inner block when an explicit boundary makes the phase clearer or inference cannot shorten it enough.
- Reborrow for a later phase instead of holding one reference across unrelated work.
- Read a borrow-checker diagnostic as evidence that two access phases overlap, then repair the phase boundary rather than bypassing it.

## Don't
- Don't expect a mutable reference to coexist with other active access to the same place merely because execution is single-threaded.
- Don't keep a shared reference alive for possible later use when mutation must happen first.
- Don't reach for cloning, raw pointers, or interior mutability solely to avoid arranging ordinary borrows into non-overlapping phases.

## Checklist
- Where is each borrow's actual last use?
- Can reads finish before the exclusive update begins?
- Does a stored reference extend the borrow farther than intended?
- Would an explicit inner block clarify the phase boundary?

## Notes
Rust's practical rule is about active access, not simply matching braces: many shared borrows may coexist, while mutation requires exclusive access to the affected place. Current borrow checking can end a borrow at its last use, so the first repair is usually to shorten the live range rather than to create a larger architectural workaround.

