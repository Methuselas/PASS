---
object_id: PAT_use_rust_wildcard_arms_only_for_intentionally_equivalent_cases
object_type: pattern
name: Use Rust Wildcard Arms Only for Intentionally Equivalent Cases
library_path: [software-engineering, languages, rust, enums-and-patterns]
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, patterns, wildcard, match, exhaustiveness]
cross_links:
- rel: related_to
  target_object_id: PAT_handle_enums_exhaustively
- rel: related_to
  target_object_id: PAT_decide_the_else_instead_of_omitting_it
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: medium
references: []
variants: []
---

# Use Rust Wildcard Arms Only for Intentionally Equivalent Cases

## Pattern Rule
**IF** every value not named by earlier Rust match arms truly has the same behavior and future values should inherit it
**THEN** finish with a wildcard or catch-all binding
**ELSE** enumerate closed-domain variants explicitly so additions produce a non-exhaustive-match error.

## Do
- Put specific patterns before a wildcard because the first matching arm wins.
- Use `_` when the remaining value is irrelevant, or a binding when the shared fallback needs the unmatched value.
- Keep explicit arms for every variant when a new variant should trigger a design decision.
- State the fallback behavior in the arm rather than relying on an omitted branch.

## Don't
- Don't add `_` solely to silence an exhaustiveness error before deciding what the missing cases mean.
- Don't hide variants you own behind a wildcard when their behavior is likely to diverge.
- Don't bind a catch-all value if the arm intentionally ignores it.

## Checklist
- Are all remaining values semantically equivalent here?
- Should future variants automatically receive the same behavior?
- Does arm order place every special case before the catch-all?
- Would explicit variants make a future change safer?

## Notes
A wildcard makes a match exhaustive by accepting every remaining value. That is a semantic promise about present and future cases, not boilerplate disposal.

