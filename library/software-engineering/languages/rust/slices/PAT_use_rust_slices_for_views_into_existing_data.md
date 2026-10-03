---
object_id: PAT_use_rust_slices_for_views_into_existing_data
object_type: pattern
name: Use Rust Slices for Views Into Existing Data
library_path: [software-engineering, languages, rust, slices]
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, slices, borrowing, api_design, utf8]
cross_links:
- rel: related_to
  target_object_id: PAT_make_misuse_impossible_by_removing_invalid_states
- rel: related_to
  target_object_id: PAT_convey_usage_through_names_and_types
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: medium
references: []
variants: []
---

# Use Rust Slices for Views Into Existing Data

## Pattern Rule
**IF** a Rust input or result is a contiguous borrowed view into existing text or elements
**THEN** express it as `&str`, `&[T]`, or a mutable slice instead of an owned container or detached numeric bounds
**ELSE** return owned data or explicit positions when independence or the positions themselves are the contract.

## Do
- Accept `&str` for read-only text APIs so callers can pass string literals, slices, or borrowed `String` contents.
- Accept `&[T]` for read-only sequential data when the function does not need a vector's ownership or capacity-changing operations.
- Return a slice when the result means “this region of the input,” tying its validity to the borrowed source through the type system.
- Treat string ranges as byte offsets and cut only at UTF-8 code-point boundaries; use character or grapheme-aware processing when the contract is about human text units.

## Don't
- Don't return a bare index or index pair for a view if mutation can make those numbers stale while the type still appears valid.
- Don't require `&String` or a reference to an owned vector when the operation needs only its contents as a slice.
- Don't assume arbitrary byte positions are valid boundaries for `str`; invalid slicing panics.
- Don't claim a slice owns or extends the lifetime of its underlying data.

## Checklist
- Is this value a view, an owned result, or a position?
- Can the parameter accept a slice instead of a specific owned collection type?
- Does the returned borrow prevent mutation that would invalidate the view?
- Are text boundaries defined in bytes, scalar values, or grapheme clusters?

## Notes
A slice packages a pointer and length under a borrow, so the compiler can connect a derived view to the source data it depends on. That relationship eliminates the stale-index state that occurs when positions are returned separately and the source changes before they are reused.
