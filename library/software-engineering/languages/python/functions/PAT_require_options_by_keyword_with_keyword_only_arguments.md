---
object_id: PAT_require_options_by_keyword_with_keyword_only_arguments
object_type: pattern
name: Require Options by Keyword with Keyword-Only Arguments
library_path:
- software-engineering
- languages
- python
- functions
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- functions
- arguments
- keyword-only
cross_links:
- rel: related_to
  target_object_id: PAT_collect_arguments_with_stars_in_a_header_and_unpack_them_at_a_call
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Require Options by Keyword with Keyword-Only Arguments

## Pattern Rule
**IF** a function takes both data to process and options that configure how it processes, and an option must never be filled in by a stray positional value
**THEN** make those options keyword-only by placing them after `*name` or after a bare `*` in the header, so callers have to name them, and give them defaults where they are optional
**ELSE** when the value is genuinely part of what the function operates on rather than a setting that governs it, leave it an ordinary parameter so callers may pass it either way

## Do
- Write the header as data first and options after the star — a function that takes any number of items plus a named flag can then never mistake an item for the flag, however many items arrive.
- Use a bare `*` when no extra positional arguments should be accepted at all but the following names must still be passed by name.
- Give a keyword-only argument a default to make it optional, and leave the default off to make naming it mandatory; both forms sit after the star.
- Let the signature do the validation: an unexpected keyword raises on its own, where a function that swept every keyword into one collecting parameter would ignore the stray silently unless it removed each expected key and checked what remained.
- Reach for the positional-only marker `/` for the opposite constraint, when parameters before it should never be passed by name because their names are an implementation detail callers must not bind to.

## Don't
- Don't place keyword-only names after the arbitrary-keywords parameter, and don't write a bare double star; both are syntax errors, since the collecting keywords form must come last.
- Don't assume a parameter written before the star is keyword-only; anything ahead of it remains an ordinary parameter that a caller may pass positionally, even when it has a default.
- Don't hand-roll option checking by removing expected keys from a collected dict and raising on the leftovers when keyword-only parameters state the same contract in the signature itself.
- Don't make an argument keyword-only just because it has a default; optional and keyword-only are separate decisions, and forcing names on ordinary arguments makes ordinary calls wordier.

## Checklist
- Could any option in this signature be filled in accidentally by an extra positional argument?
- Is each keyword-only name's optionality expressed by the presence or absence of a default?
- Does the header keep the collecting keywords form last?
- Where callers must not depend on a parameter's name, is the positional-only marker used rather than a comment asking them not to?

## Notes
The benefit is that a contract moves out of the body and into the signature: without keyword-only parameters, a function that wants both arbitrary data and named options has to collect everything and then police the options itself, which is more code and silently forgiving of typos in option names. The complementary marker for positional-only parameters arrived in a later release than this material describes, so a reader comparing the two should expect the star to be the older and more widely seen of the pair.
