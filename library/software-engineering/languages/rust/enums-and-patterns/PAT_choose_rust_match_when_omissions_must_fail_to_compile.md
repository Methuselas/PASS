---
object_id: PAT_choose_rust_match_when_omissions_must_fail_to_compile
object_type: pattern
name: Choose Rust Match When Omissions Must Fail to Compile
library_path: [software-engineering, languages, rust, enums-and-patterns]
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, match, if_let, patterns, exhaustiveness]
cross_links:
- rel: related_to
  target_object_id: PAT_handle_enums_exhaustively
- rel: related_to
  target_object_id: AP_shape_a_multi_way_decision
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: medium
references: []
variants: []
---

# Choose Rust Match When Omissions Must Fail to Compile

## Pattern Rule
**IF** behavior must account for every possible shape of a Rust value, including future variants that should force review
**THEN** use `match`, enumerate the closed-domain cases explicitly, and preserve exhaustive checking
**ELSE** use `if let` or `let else` when one refutable pattern is the meaningful case and all nonmatches deliberately share one outcome.

## Do
- Use `match` when several variants produce different results or when every variant deserves an explicit decision.
- Bind payload fields in the arm pattern that owns them and keep the arm result compatible with the whole expression's type.
- Use `if let` for a focused success or action path whose remaining cases are intentionally ignored or handled together.
- Use an `if let` chain when several pattern matches and Boolean guards form one short-circuit condition and the project uses an edition that supports let chains.
- Use `let else` when one pattern is required for the following scope and failure should diverge immediately by returning, breaking, continuing, or panicking.

## Don't
- Don't trade away exhaustive checking merely to remove a small amount of syntax.
- Don't expand a single meaningful pattern into a ceremonial match with an empty catch-all arm.
- Don't use conditional pattern syntax when different nonmatching variants need different behavior.

## Checklist
- Must a newly added enum variant force this code to be reviewed?
- Do multiple cases have distinct behavior or results?
- Is there exactly one useful pattern and one shared nonmatch outcome?
- Do several dependent pattern checks belong to one short-circuit condition?
- Should the bound values remain available after the conditional succeeds?

## Notes
All three constructs destructure with patterns, but they encode different maintenance contracts. `match` makes coverage part of compilation; `if let` chooses one conditional branch; `let else` establishes bindings for the continuation or leaves it.
