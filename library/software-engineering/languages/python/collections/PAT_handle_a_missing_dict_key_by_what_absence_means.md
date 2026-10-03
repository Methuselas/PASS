---
object_id: PAT_handle_a_missing_dict_key_by_what_absence_means
object_type: pattern
name: Handle a Missing Dict Key by What Absence Means
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
- defaults
- keyerror
- sparse-data
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

# Handle a Missing Dict Key by What Absence Means

## Pattern Rule
**IF** Python code looks up a dictionary key that may not be present
**THEN** pick the lookup by what a missing key means: a default value (`d.get(k, default)`), a different branch (`if k in d:`), an error in the data (`d[k]` inside `try`/`except KeyError`), or an entry to create on first use (`setdefault`, `collections.defaultdict`, `collections.Counter`)
**ELSE** when every key is guaranteed present by construction, index directly with `d[k]` and let a `KeyError` expose the broken guarantee.

## Do
- Read with a default when absence is normal: `count = totals.get(name, 0)`. The same call represents sparse data cheaply — a dict keyed by `(x, y, z)` tuples holds only the filled cells, and `grid.get((x, y, z), 0)` reads the rest as zero.
- Branch with `in` when the missing case needs different code, not just a different value.
- Let `KeyError` propagate, or catch it at a boundary and report the bad key, when the key must exist and its absence is a defect in the input.
- Group items with `groups.setdefault(key, []).append(item)`, or a `defaultdict(list)` when the whole dictionary is built that way; count with `Counter(items)`.
- Remove an entry that may be absent with `d.pop(k, None)`.
- Use a private sentinel, `_MISSING = object()` and `d.get(k, _MISSING) is _MISSING`, when `None` is itself a stored value.

## Don't
- Don't use `d.get(k)` and then test the result for `None` when `None` can be a stored value; a present key and a missing key look the same.
- Don't read from a `defaultdict` to test membership: `g['b']` inserts `'b'` with an empty default. Test with `'b' in g`.
- Don't write `d.has_key(k)`; it was removed in Python 3. Use `k in d`.
- Don't wrap lookups in `try` blocks that are wide enough to catch a `KeyError` raised by some other dictionary inside the block.

## Checklist
- For each lookup that can miss, is the chosen form the one that matches what absence means here?
- Can `None` be a stored value, and if so does the code tell it apart from a missing key?
- Is any `defaultdict` being read in a way that silently adds keys?

## Notes
Dictionaries are hash tables mapping hashable keys to values; lookup by key does not scan, which is why dictionaries replace hand-coded search structures and why integer or tuple keys make convenient sparse arrays that grow on assignment where a list would raise `IndexError`. Keys must be immutable — strings, numbers, tuples of immutables — because a key that could change would no longer hash to where it was stored.
