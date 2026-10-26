---
object_id: PAT_substitute_rust_placeholders_by_exact_region_not_whole_tokens
object_type: pattern
name: Substitute Rust Placeholders by Exact Region, Not Whole Tokens
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
- templates
- substitution
- replace
- injection
cross_links:
- rel: related_to
  target_object_id: PAT_classify_tag_keywords_within_their_delimited_region
reference:
  source_title: Practical System Programming for Rust Developers
  author: Prabhu Eshwarla
confidence: high
references: []
variants: []
---

# Substitute Rust Placeholders by Exact Region, Not Whole Tokens

## Pattern Rule
**IF** implementing placeholder substitution - replacing each occurrence of a delimited marker in text with a looked-up value
**THEN** target the exact delimited region of each placeholder, resolve values before inserting them into the output, and build the result in a single pass so substituted values are never rescanned by later lookups.

## Do
- Match the placeholder by its delimiters (the region between the marker pairs), not by the whole whitespace-delimited word: a word like '{{name}}.' carries trailing punctuation that a word-level replace consumes along with the placeholder.
- Build the output incrementally - copy literal text up to each placeholder, append the resolved value, continue past the region - so each input byte is classified once and values enter only as final output.
- Decide the missing-key policy at the API boundary (error, empty, or keep-the-placeholder) and return Option/Result accordingly; a bare unwrap makes one absent context key abort the whole render.
- Test the adversarial trio: placeholder glued to punctuation, missing key, and a substituted value that contains placeholder syntax for a later key.

## Don't
- Don't substitute by repeated string replace of whole collected tokens over the shrinking output: the reference implementation's own headline example renders 'Hello Bob Are you from Boston' - the period and question mark vanish because the tokens it matched were '{{name}}.' and '{{city}}?'.
- Don't run later replacements over text already containing substituted values: with input '{{name}} {{city}}' and name set to another placeholder, sequential replacement yields the second key's value twice - the injected value was replaced again by the second lookup.
- Don't let the context lookup panic on absence: context data comes from users and config files, so a miss is expected input, not a broken invariant.

## Checklist
- Does substitution target the delimiter region exactly, preserving adjacent punctuation?
- Is the result built in one pass so no substituted value is ever rescanned?
- Is the missing-key behavior an explicit, documented, tested policy?
- Do the tests include placeholder-adjacent punctuation and placeholder-syntax values?

## Notes
Three failures reproduced verbatim from the source implementation on rustc 1.98.1: (1) the book's own example input renders 'Hello Bob Are you from Boston' instead of its advertised 'Hello Bob. Are you from Boston?' because whitespace-token collection kept the punctuated forms as the replacement patterns; (2) a context map missing one key aborts the render via unwrap on None; (3) one context value holding another key's placeholder injects a second substitution - both output positions become the second value - because replacements run over the already-substituted string.

Single-pass construction fixes all three structurally: punctuation outside the delimiter region is copied verbatim, values are appended as terminal text and never matched again, and the lookup result (Option) is handled at the one place the policy lives. The same shape - classify region, emit once, never rescan - is the substitution counterpart of the region-scoped classification rule.
