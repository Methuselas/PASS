---
object_id: PAT_prove_rust_raw_pointer_ranges_before_forming_references
object_type: pattern
name: Prove Rust Raw-Pointer Ranges Before Forming References
library_path: [software-engineering, languages, rust, unsafe]
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, unsafe, raw_pointers, slices, aliasing]
cross_links:
- rel: related_to
  target_object_id: PAT_confine_rust_unsafe_to_a_documented_safe_abstraction
- rel: related_to
  target_object_id: PAT_end_conflicting_rust_borrows_before_mutation
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
references: []
variants: []
---

# Prove Rust Raw-Pointer Ranges Before Forming References

## Pattern Rule
**IF** Rust code must dereference raw pointers or construct references or slices from raw parts
**THEN** prove the allocation, bounds, alignment, initialization, lifetime, and aliasing conditions for the entire resulting range before the unsafe conversion
**ELSE** keep using references, slices, and their safe splitting or indexing operations.

## Do
- Derive raw pointers from a live allocation or reference whose origin and extent you can trace; preserve the allocation for the full lifetime of every reference reconstructed from it.
- Check arithmetic against element counts and allocation bounds before computing a pointer or length, and use the pointer operation whose contract matches the intended movement.
- Prove that every byte covered by a reconstructed value is properly aligned and initialized for its target type.
- For shared references, prove that no mutation forbidden by Rust occurs while they live; for mutable references, prove exclusive access to every covered element for the full borrow.
- When splitting a mutable slice, prove the split point is in bounds and that the two output ranges do not overlap before calling `from_raw_parts_mut`.
- Keep pointer creation separate from dereference: creating a raw pointer may be safe, but using it does not acquire validity from the cast itself.

## Don't
- Don't infer that a non-null address is valid, aligned, initialized, live, or permitted for the requested access.
- Don't create overlapping mutable references or a mutable reference that overlaps a live shared reference, even when the code happens to run on one thread.
- Don't let the owner move, reallocate, or drop storage while a reconstructed reference or slice remains usable.
- Don't use a large unsafe block when only one pointer arithmetic or raw-parts construction needs the assertion.

## Checklist
- Which live allocation owns this address, and how large is the proven range?
- Is the pointer aligned and the full target range initialized?
- Does the computed offset stay within the operation's required bounds?
- Who can read or write the same memory while the resulting reference lives?
- What prevents reallocation or destruction before that lifetime ends?

## Notes
Raw pointers can be created in safe code and may be null, dangling, misaligned, or aliased. The unsafe step is where code dereferences one or asserts enough facts to create a reference or slice. That assertion must cover the whole target range, not only the first address.

The familiar safe `split_at_mut` shape illustrates the method: obtain one raw base pointer and the original length, reject a midpoint beyond the length, then construct two mutable slices over disjoint ranges. The safe return type is justified only because the implementation proves the conditions that the raw-parts constructor cannot check.
