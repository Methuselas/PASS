---
object_id: PAT_classify_tag_keywords_within_their_delimited_region
object_type: pattern
name: Classify Tag Keywords Within Their Delimited Region
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
- classification
- keywords
- word_boundaries
cross_links:
- rel: related_to
  target_object_id: PAT_slice_embedded_regions_with_ordered_delimiter_searches
- rel: related_to
  target_object_id: PAT_use_rust_wildcard_arms_only_for_intentionally_equivalent_cases
reference:
  source_title: Practical System Programming for Rust Developers
  author: Prabhu Eshwarla
confidence: high
references: []
variants: []
---

# Classify Tag Keywords Within Their Delimited Region

## Pattern Rule
**IF** lines or statements must be classified into syntax kinds by keywords (for, if, end) embedded in a delimited region
**THEN** first extract the delimited region, then compare the region's keyword position at word-boundary granularity (split into words and compare whole words), never by substring containment over the whole input.

## Do
- Restrict keyword matching to the interior of the delimiters so free text elsewhere in the line cannot trigger a classification.
- Compare whole words (`split_whitespace`, or a word-boundary scan) so `gift` never satisfies `if` and `iffy` never satisfies `if`.
- Test the classification with adversarial content: keywords embedded inside unrelated words, keywords appearing in literal text outside the delimiters, and combined keywords (`for` together with `in`).
- Make the classifier total: every input yields exactly one kind, with an explicit unrecognized or literal outcome, so the caller's match is exhaustive and debuggable.
- Order the classification checks deliberately when kinds can both match, and document that ordering as part of the grammar rather than leaving it to if-else sequence luck.

## Don't
- Don't classify with `input.contains("if")`: verified that a reference template classifier tagged `{% let gift = 1 %}` and `{% iffy %}` as if-tags because `gift` and `iffy` contain the substring `if`.
- Don't scan the entire input for keywords that belong to a delimited region; the region exists precisely to scope the grammar.
- Don't rely on check order alone to disambiguate kinds when a single input can satisfy two kinds' predicates; tighten the predicates instead and treat the ordering as documentation.
- Don't let an unclassified input fall silently into the literal kind when it contains a malformed delimiter pair; malformed syntax deserves its own outcome so callers can report it.

## Checklist
- Are keywords matched only inside the delimited region, as whole words?
- Do adversarial inputs (`gift`, `iffy`, keyword in literal text) classify correctly?
- Is the classifier total, with a distinct outcome for malformed pairs versus plain literals?
- When two kinds could match, is the precedence explicit and tested?

## Notes
Substring containment answers 'does this text appear', not 'is this the syntax'. Template grammars are small enough that the shortcut looks safe and then misfires on ordinary English and ordinary identifiers: verified misclassifications include a tag whose only word was `iffy` and an unrelated `let gift = 1` tag - both became if-tags because their text merely contains `if`.

The durable shape is two-stage: extract the region (ordered delimiter search), then interpret it (whole-word compare on the region's keyword slot). The first stage cannot misread keywords and the second cannot misread delimiters; each stage is testable in isolation and the adversarial inputs for one stay out of the other's tests.
