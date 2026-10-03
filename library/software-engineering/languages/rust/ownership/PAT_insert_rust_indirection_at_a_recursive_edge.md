---
object_id: PAT_insert_rust_indirection_at_a_recursive_edge
object_type: pattern
name: Insert Rust Indirection at a Recursive Edge
library_path: [software-engineering, languages, rust, ownership]
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, recursive_types, box, indirection, layout]
cross_links:
- rel: related_to
  target_object_id: PAT_choose_rust_smart_pointer_by_ownership_contract
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
references: []
variants: []
---

# Insert Rust Indirection at a Recursive Edge

## Pattern Rule
**IF** a Rust type contains itself directly and therefore has no finite compile-time size
**THEN** replace the recursive field with a fixed-size indirection whose ownership matches that edge, using `Box&lt;Self&gt;` when the parent exclusively owns the recursive value
**ELSE** keep direct fields when their complete layout is finite and known.

## Do
- Locate the edge that recurses into the same type; one indirection on that path is enough to make the containing layout finite.
- Use `Box&lt;T&gt;` when the parent owns the nested value exclusively and no shared lifetime or runtime interior mutation is required.
- Choose a different indirection only because the edge has a different ownership contract, not merely because several pointer types satisfy the compiler's size error.
- Keep the non-recursive base case explicit so construction and traversal have a finite stopping condition.
- Reconsider whether a recursive representation is warranted when a standard collection already expresses the required sequence or tree operations.

## Don't
- Don't store the recursive value directly and expect the compiler to infer a maximum depth; the type must describe one layout that works for every value.
- Don't read heap allocation as the point of the repair. The decisive property is a pointer-sized boundary that breaks the layout equation.
- Don't select `Rc&lt;T&gt;` for a singly owned edge only because the compiler suggested it as one possible indirection.

## Checklist
- Which field creates the recursive layout cycle?
- Does the chosen indirection have a known size?
- Does its ownership behavior match the relationship between the nodes?
- Is the base case explicit?
- Would a standard collection make the custom recursion unnecessary?

## Notes
For a direct recursive enum, computing the size of one value requires computing the size of another value of the same type without end. A fixed-size pointer breaks that calculation. `Box&lt;T&gt;` is the minimal choice when indirection and exclusive ownership are the only capabilities the recursive edge needs.
