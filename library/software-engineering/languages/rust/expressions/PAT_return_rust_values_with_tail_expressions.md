---
object_id: PAT_return_rust_values_with_tail_expressions
object_type: pattern
name: Return Rust Values With Tail Expressions
library_path: [software-engineering, languages, rust, expressions]
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, expressions, functions, blocks, return_values]
cross_links: []
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: medium
references: []
variants: []
---

# Return Rust Values With Tail Expressions

## Pattern Rule
**IF** a Rust block or function should yield its final computed value normally
**THEN** make that value the block's final expression without a trailing semicolon
**ELSE** use explicit `return` for an early exit or end with a statement when the intended value is unit `()`.

## Do
- Read the final line of a value-producing block as part of its type contract: every reachable branch must yield a compatible type.
- Use expression-valued `if` or `match` directly where the selected branch computes one binding.
- Keep explicit `return` for control flow that exits before the natural end; it need not decorate the normal tail path.
- Diagnose an unexpected `()` by checking whether a semicolon converted the intended tail expression into a statement.

## Don't
- Don't add semicolons mechanically to the last expression of a value-producing block.
- Don't make different branches yield unrelated types and expect the receiving binding to acquire a runtime-dependent type.
- Don't hide a complex early-exit structure merely to avoid writing `return`.

## Checklist
- Does the declared or inferred result type match the tail expression?
- Do all value-producing branches converge on a compatible type?
- Is an unexpected unit value caused by a trailing semicolon?
- Are early exits explicit while the normal result remains visible at the tail?

## Notes
Blocks are expressions in Rust, so punctuation participates in meaning: `value` yields that value, while `value;` performs a statement and leaves `()`. This is why a one-character edit can turn a valid return into a type mismatch.

