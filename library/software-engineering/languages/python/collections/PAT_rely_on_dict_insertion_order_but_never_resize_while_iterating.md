---
object_id: PAT_rely_on_dict_insertion_order_but_never_resize_while_iterating
object_type: pattern
name: Rely on Dict Insertion Order but Never Resize While Iterating
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
- dictionaries
- ordering
- iteration
- views
cross_links:
- rel: related_to
  target_object_id: PAT_handle_a_missing_dict_key_by_what_absence_means
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Rely on Dict Insertion Order but Never Resize While Iterating

## Pattern Rule
**IF** Python code walks a dictionary's keys, values or items, or depends on the order they come out in
**THEN** rely on insertion order, which the language guarantees, sort explicitly only when you need key order, and iterate over a snapshot (`list(d)`) whenever the loop adds or removes keys
**ELSE** when two dictionaries must compare unequal because their order differs, or the code needs `move_to_end`, use `collections.OrderedDict`.

## Do
- Iterate a dictionary directly — `for key in d`, `for key, value in d.items()` — and expect the order in which the keys were first inserted. Reassigning an existing key keeps its position; deleting and re-adding moves it to the end.
- Use `sorted(d)` or `sorted(d.items())` when output must be in key order.
- Delete while scanning by iterating over a copy: `for k in list(d): if drop(k): del d[k]`, or rebuild with a comprehension, `d = {k: v for k, v in d.items() if keep(k)}`.
- Use key views for set algebra between dictionaries: `d1.keys() & d2.keys()` gives the shared keys, and `d1.keys() - d2.keys()` those only in `d1`.
- Merge into a new dictionary with `d1 | d2`, or in place with `d1 |= d2` or `d1.update(d2)`; later values win.

## Don't
- Don't add or delete keys inside a loop over the dictionary or one of its views; Python raises `RuntimeError: dictionary changed size during iteration`.
- Don't keep a view (`d.keys()`, `d.values()`) as if it were a snapshot; views reflect later changes. Call `list()` on it to freeze the contents.
- Don't index a view (`d.keys()[0]`) or call `.sort()` on one; views are not lists. Use `next(iter(d))` for the first key and `sorted()` for ordering.
- Don't reach for `OrderedDict` just to keep insertion order; a plain `dict` already does.

## Checklist
- Does any loop over a dictionary add or remove keys?
- Where order matters, is it insertion order or key order, and is the code using the matching tool?
- Is any view stored and read later as though it could not change?

## Notes
Dictionaries preserve insertion order as a language guarantee since Python 3.7; older material describing dictionary order as arbitrary or scrambled predates that change. `keys()`, `values()` and `items()` return live views: iterable, sized, and — for keys, and for items whose values are hashable — set-like. Equality between plain dictionaries ignores order; between `OrderedDict` objects it does not.
