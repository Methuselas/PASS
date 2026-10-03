---
object_id: PAT_put_relational_rust_pattern_conditions_in_match_guards
object_type: pattern
name: Put Relational Rust Pattern Conditions in Match Guards
library_path: [software-engineering, languages, rust, enums-and-patterns]
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: PAT_order_branches_so_the_common_case_is_found_first
tags: [rust, patterns, match_guards, bindings, control_flow]
cross_links:
- rel: related_to
  target_object_id: PAT_choose_rust_match_when_omissions_must_fail_to_compile
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
references: []
variants: []
---

# Put Relational Rust Pattern Conditions in Match Guards

## Pattern Rule
**IF** a Rust match arm needs both a structural shape and a Boolean or dependent-pattern condition that the pattern syntax cannot express
**THEN** bind the required pieces with distinct names, place the extra condition in a match guard, and retain a fallback for values whose structure matches but whose guard fails
**ELSE** keep the decision entirely in the pattern so exhaustiveness and overlap remain visible to the compiler and reader.

## Do
- Use the pattern for variants, literals, ranges, and destructuring, then use the guard for comparisons with outer values or relationships among bound fields.
- Choose binding names that do not accidentally shadow an outer value the guard must read.
- Use `name @ subpattern` when the arm needs the whole value that also satisfied a literal, range, variant, or nested pattern.
- Remember that a guard after alternatives applies to the entire `p1 | p2` pattern, not only to its final alternative.
- Put an unguarded arm after guarded refinements when the same structural case still needs a general behavior.

## Don't
- Don't use a fresh identifier pattern when you meant to compare with an outer variable; a pattern identifier binds and shadows rather than testing equality.
- Don't rely on a guarded arm to cover a variant for exhaustiveness. The guard can fail, so another arm must cover the remaining values.
- Don't give guards surprising side effects. Alternative patterns may cause guard evaluation more than once before the match continues.
- Don't move a condition into a guard when a literal, range, or nested structural pattern states it more directly.

## Checklist
- Which facts are structural and which require evaluation?
- Does any pattern binding shadow a value the guard intends to compare?
- What handles the same shape when the guard is false?
- Does an `@` binding make both the tested shape and captured value explicit?
- Could guard evaluation have side effects or run more than once across alternatives?

## Notes
A successful structural pattern makes its bindings available to the guard, but the arm is selected only when the guard also succeeds. If the guard fails, matching continues with later patterns. The matched value is not moved into a binding merely for a guard that fails, which permits guards to inspect borrowed bindings before the selected arm performs its move or copy.
