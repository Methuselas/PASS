---
object_id: PAT_keep_rust_iterator_exhaustion_distinct_from_item_failure
object_type: pattern
name: Keep Rust Iterator Exhaustion Distinct From Item Failure
library_path:
- software-engineering
- languages
- rust
- iterators
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- rust
- iterators
- result
- errors
- parsing
cross_links:
- rel: related_to
  target_object_id: PAT_define_custom_rust_iterators_as_next_state_transitions
- rel: related_to
  target_object_id: PAT_keep_rust_failures_as_result_until_recovery_context_exists
reference:
  source_title: Practical System Programming for Rust Developers
  author: Prabhu Eshwarla
confidence: medium
references: []
variants: []
---

# Keep Rust Iterator Exhaustion Distinct From Item Failure

## Pattern Rule
**IF** producing the next Rust iterator item can fail independently of reaching the end of the sequence
**THEN** reserve `None` for exhaustion and carry item-level failure in the item type, typically as a `Result` whose success value is the item and whose error value describes the failure

## Do
- Use `Option` at the iterator boundary to mean whether another item exists.
- Use `Result` inside the item when a present input element can be malformed, unreadable, or otherwise fail to decode.
- Preserve the error value long enough for the consumer to decide whether to stop, report, skip, or recover.
- Test normal exhaustion separately from malformed-item behavior.

## Don't
- Don't return `None` for both invalid input and end of input; consumers cannot tell why iteration stopped.
- Don't invent an ordinary data item solely to represent end-of-iteration when the `Iterator` contract already has `None`.
- Don't hide a fallible conversion behind `unwrap` when malformed external input is part of the iterator's domain.

## Checklist
- Does `None` mean only that no more items exist?
- Can a malformed item be distinguished from clean exhaustion?
- Does the item type preserve the failure detail a caller may need?
- Are exhaustion and failure tested as separate cases?

## Notes
A tokenizer is a common place to expose this distinction: the character stream can end normally, while a character or numeric lexeme can also fail validation. Modeling those as different states keeps the standard iterator contract meaningful and prevents silent truncation.
