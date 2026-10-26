---
object_id: PAT_slice_embedded_regions_with_ordered_delimiter_searches
object_type: pattern
name: Slice Embedded Regions with Ordered Delimiter Searches
library_path:
- software-engineering
- languages
- rust
- parsing
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- rust
- parsing
- strings
- slicing
- delimiters
cross_links:
- rel: related_to
  target_object_id: PAT_process_rust_text_at_the_boundary_the_domain_means
- rel: related_to
  target_object_id: PAT_climb_precedence_by_raising_the_minimum_on_the_right
reference:
  source_title: Practical System Programming for Rust Developers
  author: Prabhu Eshwarla
confidence: high
references: []
variants: []
---

# Slice Embedded Regions with Ordered Delimiter Searches

## Pattern Rule
**IF** a text region delimited by an opening and a closing delimiter pair must be extracted from a larger string (template variables, quoted spans, embedded markup)
**THEN** locate the pair in one ordered pass - find the opening, then find the closing starting after the opening plus its width - and slice with the found byte offsets and each delimiter's `len()`, never with independent containment checks or fixed index arithmetic.

## Do
- Use `find` (or `split_once`) which returns byte offsets valid for slicing on ASCII delimiters, and chain the closing search from the position after the opening delimiter so the pair is ordered by construction.
- Derive every width from the delimiter itself (`open.len()`), so changing a one-character delimiter to a two-character one cannot leave stale arithmetic behind.
- Return `Option` or `Result` when the pair is absent or misordered; string slicing with start greater than end is a panic, not a recoverable value.
- Treat indices from `char_indices` and `find` as byte offsets: they are correct slice points but wrong character counts - never mix them with character-count arithmetic.
- Test the adversarial shapes directly: reversed pair (closing before opening), single delimiter occurrence, nested and doubled delimiters, and non-ASCII characters before and inside the region.

## Don't
- Don't validate a region with `contains(open) && contains(close)`: that accepts `}} ... {{`, reversed, and the extraction that follows slices out of order - verified to panic with 'slice index starts at 5 but ends at 0'.
- Don't hardcode delimiter widths as index arithmetic (`i + 1 + 1`): applied to a single-brace input it silently returns a truncated variable (`{name}` yields `ame`) instead of failing.
- Don't split the search for the opening and the closing delimiter into independent full-string scans; the two results carry no ordering guarantee relative to each other.
- Don't return a sentinel like `(false, 0)` from an index helper and let callers slice with it; absence must stop the caller, not become index zero.

## Checklist
- Is the closing delimiter searched only after the opening delimiter's end position?
- Do all offsets come from `find`/`char_indices` byte offsets and `len()` of the actual delimiters?
- Does a reversed or unmatched pair produce `None`/`Err` instead of a panic or silent truncation?
- Are reversed-pair, single-occurrence, and non-ASCII inputs in the tests?

## Notes
Extraction is one search with state, not two independent predicates. `split_once` is the smallest honest API: it returns the parts around the first occurrence of a delimiter, and nesting it (split once at the opening, then split the remainder at the closing) makes misordering impossible rather than merely unlikely. Byte offsets are the correct currency: Rust string slices index by bytes, and `find` on ASCII delimiters lands exactly on boundaries.

Verified against a reference template-engine helper built from two full-string containment checks plus a character-index helper returning `(false, 0)` on absence and hardcoded `i + 1 + 1` widths: the reversed input `}} {{name}}` panicked inside the extractor (exit 101), and single-brace input `{name}` silently yielded the variable `ame`. Both failures are invisible to the happy path and visible to any ordered-search rewrite.
