---
object_id: PAT_compose_parsers_from_small_rules
object_type: pattern
name: Compose Parsers From Small Rules
library_path:
- software-engineering
- core
- modularity
stage_binding: 2 block
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- parsing
- protocols
- composition
- grammar
- modularity
cross_links: []
reference:
  source_title: Network Programming with Rust
  author: Abhishek Chanda
confidence: medium
references: []
variants: []
---

# Compose Parsers From Small Rules

## Pattern Rule
**IF** structured input has several independently recognizable fields, tokens, or subforms
**THEN** write small parsers for those local rules and compose them into the larger grammar so each boundary and failure stays explicit
**ELSE** for a trivial fixed input with no reusable substructure, use the simplest direct parse that still makes invalid input observable

## Do
- Give each subparser one recognizable responsibility, such as a method token, delimiter, field, numeric component, or fixed-width segment.
- Compose the larger parse in the same structural order as the data format, carrying successful values forward into the result type.
- Keep parse failure and incomplete input distinct when the input source can legitimately end before a complete record arrives.
- Test the small rules independently when a composed parse fails so the failing boundary can be isolated before debugging the whole grammar.

## Don't
- Don't bury a multi-field format in one opaque scan when the same boundaries can be named and tested separately.
- Don't treat a partially recognized prefix as a complete record without an explicit policy for the unconsumed input.
- Don't tie the grammar to a particular parser library's macro or operator syntax; the transferable rule is the decomposition and composition.

## Checklist
- What are the smallest independently meaningful parse rules?
- Does the composition order match the format's actual structure?
- Can the caller distinguish invalid input from input that is merely incomplete?
- What must happen to any input left after the intended record is parsed?

## Notes
Parser combinators are one mechanism for this shape, but the design rule is broader: local recognition rules should remain small enough to test and reason about, while the complete parser states how those rules form the record.
