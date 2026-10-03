---
object_id: PAT_encode_rust_alternatives_with_data_carrying_enum_variants
object_type: pattern
name: Encode Rust Alternatives With Data-Carrying Enum Variants
library_path: [software-engineering, languages, rust, enums-and-patterns]
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, enums, sum_types, domain_modeling, invalid_states]
cross_links:
- rel: related_to
  target_object_id: PAT_make_misuse_impossible_by_removing_invalid_states
- rel: related_to
  target_object_id: PAT_encapsulate_related_data_together
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: medium
references: []
variants: []
---

# Encode Rust Alternatives With Data-Carrying Enum Variants

## Pattern Rule
**IF** a Rust value must be exactly one of a closed set of alternatives and each alternative may require different data
**THEN** represent it as one enum whose variants carry only the fields valid for that alternative
**ELSE** use a struct when the fields coexist as parts of one value rather than selecting mutually exclusive states.

## Do
- Put variant-specific payloads directly on their variants so constructing a value also proves which data is present.
- Choose named fields inside a variant when payload roles need labels and positional fields when their order is already unambiguous.
- Keep operations that apply to every variant associated with the enum, and use pattern matching where behavior differs by variant.
- Prefer an existing standard-library domain type when it already supplies the representation and invariants you need.

## Don't
- Don't model an alternative as a separate tag plus fields that are meaningful only for some tag values.
- Don't use independent structs when callers need one type that accepts every alternative.
- Don't add placeholder fields to variants that do not need that data.

## Checklist
- Can exactly one alternative be active at a time?
- Does each alternative carry only data valid for that state?
- Would a tag-plus-payload struct permit mismatched combinations?
- Is the set of alternatives intentionally closed for exhaustive handling?

## Notes
Rust enum variants are constructors of one type and may carry different payload shapes. This lets the type represent a choice and its valid data together, eliminating combinations that a separate discriminator and shared payload fields would permit.

