---
object_id: PAT_process_rust_text_at_the_boundary_the_domain_means
object_type: pattern
name: Process Rust Text at the Boundary the Domain Means
library_path: [software-engineering, languages, rust, collections]
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, strings, utf8, unicode, graphemes]
cross_links:
- rel: related_to
  target_object_id: PAT_use_rust_slices_for_views_into_existing_data
- rel: related_to
  target_object_id: PAT_convey_usage_through_names_and_types
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: medium
references: []
variants: []
---

# Process Rust Text at the Boundary the Domain Means

## Pattern Rule
**IF** a Rust text operation depends on a notion of position or element
**THEN** decide whether the domain means UTF-8 bytes, Unicode scalar values, or user-perceived grapheme clusters and use an API for that level
**ELSE** keep text as string slices or owned strings without inventing indexes.

## Do
- Use bytes for protocols and encodings defined in bytes.
- Use `chars` when Unicode scalar values are the required unit.
- Use a Unicode segmentation library when the requirement is user-perceived characters or text boundaries beyond scalar values.
- Treat string lengths and ranges as byte-based and validate slice boundaries.

## Don't
- Don't call a byte offset a character index.
- Don't assume one scalar value equals one displayed character.
- Don't slice arbitrary external offsets without a non-panicking validation path.
- Don't convert to a character vector unless repeated scalar indexing justifies the allocation and changed indexing model.

## Checklist
- What exact text unit does the requirement name?
- Are offsets measured in bytes by the producer?
- Can a range split a UTF-8 code point?
- Does the UI require grapheme-aware behavior?

## Notes
Rust strings prevent ambiguous single-index access because bytes, scalar values, and grapheme clusters are different sequences. Correctness starts by selecting the sequence the domain actually means.

