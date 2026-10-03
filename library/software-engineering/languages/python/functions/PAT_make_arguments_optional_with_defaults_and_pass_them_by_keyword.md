---
object_id: PAT_make_arguments_optional_with_defaults_and_pass_them_by_keyword
object_type: pattern
name: Make Arguments Optional with Defaults and Pass Them by Keyword
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
- defaults
cross_links: []
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Make Arguments Optional with Defaults and Pass Them by Keyword

## Pattern Rule
**IF** a function has arguments most callers will not need to set, or a call site whose bare positional values would not say what they mean
**THEN** give the optional arguments defaults in the header and pass them by name at the call, so callers supply only what differs from the default and every supplied value carries a label
**ELSE** when every argument is required and the list is short enough to read at a glance, plain positional matching is clearer than labelling each value

## Do
- Order the header with required arguments first and defaulted ones after them; the defaults are what makes that tail optional.
- Pass by name at the call to skip over defaults worth keeping, so a later argument can be set while the ones before it stay at their defaults.
- Label values with names at calls where bare positionals would be unreadable; three naked values separated by commas say nothing about which parameter each one feeds.
- Mix positional and named arguments in one call freely: positionals are matched left to right first, then names are matched to parameters, so the order among the named ones does not matter.

## Don't
- Don't read `name=value` in a header as the same construct as `name=value` in a call; in the header it supplies a default, in the call it selects which parameter receives the value, and neither one is an assignment statement.
- Don't give a default a mutable object such as a list or dict: the default object is built once when the `def` runs and reused by every later call, so a change made during one call is still there on the next.
- Don't pass the same parameter both positionally and by name in one call; matching requires that each parameter receive exactly one value and reports an error when two arrive.

## Checklist
- Does every argument that most callers will leave alone have a default?
- At this call, would a reader know what each bare positional value means, or does it need a name?
- Is any default a mutable object that will be shared across every call?
- Could any call pass one parameter twice, once by position and once by name?

## Notes
A default is evaluated once, when the `def` statement runs, not on each call. That single fact explains both halves of this pattern's reputation: it is what makes optional arguments cheap, since nothing is recomputed per call, and it is why a mutable default quietly accumulates changes across calls instead of starting fresh. Where a fresh value is needed per call, the assignment belongs in the body rather than in the header.
