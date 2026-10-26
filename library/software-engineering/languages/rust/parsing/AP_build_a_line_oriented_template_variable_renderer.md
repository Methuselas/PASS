---
object_id: AP_build_a_line_oriented_template_variable_renderer
object_type: ap
name: Build a Line-Oriented Template Variable Renderer
library_path: [software-engineering, languages, rust, parsing]
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, parsing, templates, strings, testing, library_crate]
cross_links:
- rel: supports
  target_object_id: PAT_slice_embedded_regions_with_ordered_delimiter_searches
- rel: supports
  target_object_id: PAT_classify_tag_keywords_within_their_delimited_region
- rel: supports
  target_object_id: PAT_substitute_rust_placeholders_by_exact_region_not_whole_tokens
- rel: related_to
  target_object_id: PAT_keep_rust_binary_logic_in_a_library_for_integration_tests
reference: {source_title: Practical System Programming for Rust Developers, author: Prabhu Eshwarla}
confidence: medium
references: []
variants: []
---

# Build a Line-Oriented Template Variable Renderer

## Objective
Build a small template renderer that classifies each input line, extracts delimited variable regions, substitutes values from a context map, and exposes malformed syntax and missing-data policy through testable library code.

## Steps / Flow
1. Put parser and renderer logic in a library crate and keep stdin/file handling in a thin executable boundary.
2. Define a content enum for literal text, variable expressions, supported tag kinds, and malformed or unrecognized input. Carry parsed variable data in the variant instead of re-parsing the raw line later.
3. Write table-driven tests for the normal forms before implementing helpers, then add adversarial rows for reversed or missing delimiters, keywords embedded inside larger words, punctuation adjacent to placeholders, and non-ASCII surrounding text.
4. Classify in stages: first establish whether the expected delimiter pair exists in order; only then interpret whole keywords inside that region.
5. Extract variable regions with ordered delimiter searches and delimiter-derived byte widths. Return `Option` or `Result` for malformed input instead of producing sentinel indices that callers might slice with.
6. Render in one pass: append literal text up to the placeholder, append the looked-up value, and continue after the closing delimiter. Choose the missing-variable policy explicitly and return it through the API rather than hiding it behind `unwrap` or silent omission.
7. Drive the library from the executable one line at a time. Surface malformed lines according to the chosen error policy; do not make the binary duplicate parser or renderer logic.
8. Run the full adversarial table before demonstrating the executable. The malformed cases are acceptance criteria, not optional hardening.

## Notes
The source's template-engine project cleanly exposes four separable responsibilities: classification, region extraction, context lookup, and generation. Keeping those boundaries explicit makes the common failures structural rather than mysterious: reversed delimiters cannot become slice indices, keyword substrings cannot masquerade as syntax, and inserted values are never reprocessed as template source.
