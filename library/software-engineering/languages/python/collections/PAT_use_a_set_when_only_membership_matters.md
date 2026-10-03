---
object_id: PAT_use_a_set_when_only_membership_matters
object_type: pattern
name: Use a Set When Only Membership Matters
library_path:
- software-engineering
- languages
- python
- collections
stage_binding: 3 rough
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- sets
- membership
- deduplication
- comparison
cross_links:
- rel: related_to
  target_object_id: PAT_choose_the_tables_access_scheme_by_the_key
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Use a Set When Only Membership Matters

## Pattern Rule
**IF** Python code keeps a collection only to ask whether items are in it, to drop duplicates, or to compare two groups regardless of order
**THEN** hold it in a `set` (or `frozenset` when it must be hashable), and use set operations — `in`, `&`, `|`, `-`, `^`, `<=` — instead of scanning a list
**ELSE** when order or repeat counts carry meaning, keep them with a structure that preserves them: `dict.fromkeys` for order-preserving deduplication, `collections.Counter` or `sorted` for comparisons that must count repeats.

## Do
- Track visited nodes, seen keys or processed IDs in a set; `x in seen` is a hash lookup, while `x in some_list` scans the list.
- Answer group questions with operators: `engineers & managers` for both, `engineers - managers` for only the first, `a ^ b` for exactly one, `a <= b` for subset.
- Remove duplicates while keeping first-seen order with `list(dict.fromkeys(items))`; use `set(items)` only when order is irrelevant.
- Call the method forms (`s.union(iterable)`, `s.issubset(range(...))`) when the other operand is a list, tuple or generator; the operators require both sides to be sets.
- Store compound members as tuples, and nest sets as `frozenset`; members must be hashable.

## Don't
- Don't compare two lists for "same items" with `set(a) == set(b)` when duplicates matter: `set([1, 1, 2]) == set([1, 2, 2])` is `True`. Use `Counter(a) == Counter(b)`.
- Don't write `{}` for an empty set; it is an empty `dict`. Write `set()`.
- Don't rely on the iteration order of a set, even when it looks stable in one run; sort the result for output.
- Don't try to add a list or dict to a set; they are unhashable and raise `TypeError`.

## Checklist
- Is any list here used only for `in` tests or duplicate removal?
- Where duplicates are removed, must the original order survive?
- Does each order-free comparison need to count repeats?
- Are set members hashable, with tuples or `frozenset` for compound values?

## Notes
A set is an unordered collection of unique hashable objects — in effect the keys of a dictionary without values — so membership and the set algebra run in time independent of the collection's size. Set literals (`{1, 2, 3}`) and set comprehensions (`{c * 4 for c in text}`) build them directly.

Dictionaries preserve insertion order as a language guarantee since Python 3.7, which is why `dict.fromkeys` is the order-keeping deduplicator; sets make no ordering promise at all.
