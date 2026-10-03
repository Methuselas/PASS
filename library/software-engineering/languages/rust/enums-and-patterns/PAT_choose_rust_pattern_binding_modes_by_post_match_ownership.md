---
object_id: PAT_choose_rust_pattern_binding_modes_by_post_match_ownership
object_type: pattern
name: Choose Rust Pattern Binding Modes by Post-Match Ownership
library_path: [software-engineering, languages, rust, enums-and-patterns]
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, patterns, ownership, borrowing, destructuring]
cross_links:
- rel: related_to
  target_object_id: PAT_encode_rust_ownership_intent_in_function_signatures
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
references: []
variants: []
---

# Choose Rust Pattern Binding Modes by Post-Match Ownership

## Pattern Rule
**IF** destructuring a Rust value could move a non-`Copy` field that the surrounding code still needs
**THEN** match a shared or mutable reference to the value and let the pattern bind references, using explicit `ref` or `ref mut` only in a fully explicit pattern when that makes the mixed binding contract clearer
**ELSE** destructure by value when consuming the matched value is intentional.

## Do
- Decide whether the owner must remain usable after the pattern before choosing the scrutinee and bindings.
- Match `&value` when the arm only observes fields and `&mut value` when it must mutate through the bindings; ordinary non-reference subpatterns then inherit reference binding modes through match ergonomics.
- Use `ref` or `ref mut` only when an explicit by-value pattern needs selected fields borrowed instead, and check for partial moves when other fields still bind by value.
- Use `_` for a value that must be ignored without binding, copying, moving, or borrowing it.
- Use `..` once to ignore the unneeded remainder of a struct, tuple, tuple struct, or slice while naming the parts the operation actually needs.

## Don't
- Don't assume a name beginning with `_` is a wildcard. `_name` is still an identifier binding and can move a value even though it suppresses the unused-binding warning.
- Don't add redundant `ref`, `ref mut`, or reference patterns inside an already ergonomic reference match; Rust 2024 restricts explicit modifiers outside a fully explicit prefix.
- Don't mix moved and borrowed non-`Copy` fields without accepting that the original aggregate may become partially moved and unusable as a whole.
- Don't clone a field merely to make the owner survive a match when borrowing the scrutinee expresses the real need.

## Checklist
- Is the matched owner needed after this construct?
- Does each binding become an owned value, shared reference, or mutable reference?
- Could any by-value binding partially move the aggregate?
- Is an ignored field written as `_` rather than an underscore-prefixed binding?
- Does `..` leave the intended named structure unambiguous?

## Notes
Identifier patterns use move or copy semantics by default when matching an owned value. Matching through a reference changes the default binding mode as the pattern passes through that reference, so ordinary bindings become references without spelling `ref`. The wildcard `_` is different from every identifier: it creates no binding and therefore does not copy, move, or borrow the matched value.
