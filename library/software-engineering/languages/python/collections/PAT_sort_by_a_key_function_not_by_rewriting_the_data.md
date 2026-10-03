---
object_id: PAT_sort_by_a_key_function_not_by_rewriting_the_data
object_type: pattern
name: Sort by a Key Function, Not by Rewriting the Data
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
- sorting
- lists
- key-functions
cross_links:
- rel: related_to
  target_object_id: PAT_code_to_what_an_object_can_do_not_its_type
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Sort by a Key Function, Not by Rewriting the Data

## Pattern Rule
**IF** Python code must order items by something other than their natural comparison — case-insensitively, by a field, by several fields, in descending order
**THEN** pass a `key=` function (and `reverse=True` for descending) to `sorted()` or `list.sort()`, so the sort compares derived values while the items themselves come back unchanged
**ELSE** when an ordering cannot be expressed as a key (a legacy two-argument comparison), wrap it with `functools.cmp_to_key`.

## Do
- Use `sorted(iterable, key=...)` when you need a new list or are sorting something other than a list; use `L.sort(key=...)` to reorder a list in place.
- Sort case-insensitively with `key=str.casefold` (or `str.lower` for ASCII-only text).
- Pick fields with `operator.itemgetter` or `operator.attrgetter`, or a small lambda: `key=lambda r: (r.dept, r.name)`.
- Sort on several fields in mixed directions with a tuple key that negates the numeric part, `key=lambda r: (-r[1], r[0])`, or with successive stable sorts from the least significant field to the most significant.

## Don't
- Don't write `L = L.sort()`; `sort` changes the list in place and returns `None`, so the name now refers to `None`. The same holds for `append`, `extend`, `reverse` and other in-place list methods.
- Don't pre-transform the items to sort them — `sorted(x.lower() for x in names)` returns lowered strings, not the original names.
- Don't sort a collection that mixes types without ordering between them, such as numbers and strings; Python 3 raises `TypeError` rather than inventing an order. Normalise the items or supply a key that makes them comparable.

## Checklist
- Does the sorted output contain the original items, unchanged?
- Is the result of an in-place method being assigned anywhere?
- Can the items being compared be of different types?
- For multi-field sorts, does each field sort in the intended direction?

## Notes
Python's sort is stable: items with equal keys keep their existing relative order, which is what makes sorting in several passes correct. The key function runs once per item, not once per comparison, so an expensive key costs no more than a single pass over the data.

Python 3 removed both the `cmp=` sort argument and ordering comparisons between unrelated types, which is why keys are the one supported way to customise order.
