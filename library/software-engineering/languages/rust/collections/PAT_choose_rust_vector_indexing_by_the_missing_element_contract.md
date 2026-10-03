---
object_id: PAT_choose_rust_vector_indexing_by_the_missing_element_contract
object_type: pattern
name: Choose Rust Vector Indexing by the Missing-Element Contract
library_path: [software-engineering, languages, rust, collections]
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, vec, indexing, option, panic]
cross_links:
- rel: related_to
  target_object_id: PAT_prefer_null_safety_or_optionals
- rel: related_to
  target_object_id: PAT_dont_hide_errors
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: medium
references: []
variants: []
---

# Choose Rust Vector Indexing by the Missing-Element Contract

## Pattern Rule
**IF** an absent vector position proves a violated invariant and execution cannot meaningfully continue
**THEN** use indexing and let the bounds violation panic
**ELSE** use `get` or `get_mut` and handle the optional reference when absence is expected input or control flow.

## Do
- Reserve indexing for positions already guaranteed valid by nearby logic or invariant.
- Use checked access for user-provided, stale, or otherwise uncertain positions.
- Keep the optional result visible until the missing case has a deliberate outcome.

## Don't
- Don't use checked access only to immediately unwrap an ordinary out-of-range case.
- Don't turn a broken internal invariant into silent absence.
- Don't index untrusted positions and treat a panic as input validation.

## Checklist
- Is an invalid position impossible, erroneous, or expected?
- Where is validity established?
- Can the caller recover from absence?
- Does the chosen API make that contract obvious?

## Notes
Indexing and checked access retrieve the same kind of element reference but encode different failure policies. Select the policy first.

