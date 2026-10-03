---
object_id: PAT_dispatch_a_multiway_branch_with_a_dict_instead_of_an_elif_chain
object_type: pattern
name: Dispatch a Multiway Branch with a Dict Instead of an elif Chain
library_path:
- software-engineering
- languages
- python
- control-flow
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: PAT_put_the_variation_in_data_rather_than_logic
tags:
- python
- control-flow
- dict
- dispatch
cross_links:
- rel: related_to
  target_object_id: PAT_put_the_variation_in_data_rather_than_logic
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Dispatch a Multiway Branch with a Dict Instead of an elif Chain

## Pattern Rule
**IF** selecting one of several actions based on a single Python value, with no native switch/case statement available to reach for
**THEN** choose between an `if`/`elif`/`else` chain and a dict lookup by `PAT_put_the_variation_in_data_rather_than_logic`'s general rule, and when a dict is the right choice, pick its Python-specific miss-handling mechanics deliberately: `d.get(key, default)` for a static fallback value, `key in d` when the fallback needs to do more, or `try`/`except KeyError` when a hit is the expected case and a miss is genuinely exceptional
**ELSE** when the branch count is small and fixed, or each branch does meaningfully different work rather than the same work with different values, the `if`/`elif` chain is usually the more readable choice either way

## Do
- Reach for `dict.get(key, default)` when the dictionary holds the data directly and a missing key should simply produce one fallback value.
- Reach for `key in d` followed by `d[key]` when the fallback branch needs to run more logic than returning a static default.
- Reach for `try: d[key] / except KeyError:` when the common case is a hit and the miss is the exceptional path, not just another equally likely branch.
- Store a function, bound method, or `lambda` as a dict's value when the branches are actions rather than data, and call it where an `if`/`elif` chain would otherwise call a function it picked: `table.get(choice, default)()`.

## Don't
- Don't reach for a `switch`/`case` statement; Python represents this choice only as an `if`/`elif` chain or a dict lookup, never a dedicated case construct for a single scalar key.
- Don't forget the trailing `()` when a dict's values are callables — `table[choice]` returns the function object itself, `table[choice]()` runs it, and the two are easy to conflate when some of a dict's values are plain data and others are callables meant to be invoked.
- Don't build branch logic as a string merely to make an `if`/`elif` chain "dynamic"; a dict already supports runtime construction without needing `eval`/`exec` at all.

## Checklist
- Does the dict's miss-handling (`get`, `in`, or `except KeyError`) match whether a hit or a miss is the expected case?
- If branches are actions, are the dict's values callables that get invoked, not confused with a static-data table?
- Would `PAT_put_the_variation_in_data_rather_than_logic`'s general test — how many places change when a variant is added — still favor a dict here?

## Notes
`PAT_put_the_variation_in_data_rather_than_logic` owns the general decision of when variation belongs in data rather than in control flow; this pattern is that decision's Python-specific mechanics, since Python has no switch/case statement to begin with and offers three different idioms for the one job a case statement's default clause would otherwise do.

Current Python (3.10+) also added a `match`/`case` statement for structural pattern matching, which this source predates and which this card does not cover; it is worth weighing separately when the branch is really on an object's shape or type rather than on a single scalar key.
