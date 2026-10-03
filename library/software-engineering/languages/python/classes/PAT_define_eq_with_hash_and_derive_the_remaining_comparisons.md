---
object_id: PAT_define_eq_with_hash_and_derive_the_remaining_comparisons
object_type: pattern
name: Define __eq__ with __hash__ and Derive the Remaining Comparisons
library_path:
- software-engineering
- languages
- python
- classes
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- classes
- comparison
- hashing
cross_links:
- rel: related_to
  target_object_id: PAT_compare_values_with_eq_and_reserve_is_for_singletons
- rel: related_to
  target_object_id: PAT_sort_by_a_key_function_not_by_rewriting_the_data
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Define __eq__ with __hash__ and Derive the Remaining Comparisons

## Pattern Rule
**IF** instances of a class should compare equal by their contents rather than by identity, or should be orderable
**THEN** define `__eq__`, define `__hash__` alongside it whenever instances must stay usable in sets and as dictionary keys, and generate the ordering operators from `__lt__` plus `__eq__` with `functools.total_ordering` rather than writing all six by hand
**ELSE** when the class is a plain record of fields, let `@dataclass` generate `__eq__` (and `__hash__`, with `frozen=True` or `eq=False`) instead of writing any of them

## Do
- Hash from the same values equality uses, as a tuple: `def __hash__(self): return hash((self.a, self.b))`. Objects that compare equal must hash equal, or dictionary and set lookups will miss.
- Make a value object immutable when it is hashable; mutating a field after the object has gone into a set or dict leaves it filed under a hash that no longer matches.
- Write `__lt__` and `__eq__`, then add the `@functools.total_ordering` decorator to fill in `__le__`, `__gt__` and `__ge__` consistently.
- Return `NotImplemented` — not `False`, and not an exception — when the other operand is a type you do not handle; Python then tries the reflected operation on that operand and raises a clear `TypeError` only if nothing works.
- Check the operand type before comparing (`isinstance`) so an unrelated object reaches that `NotImplemented` path rather than producing a wrong answer.

## Don't
- Don't define `__eq__` and forget `__hash__`. Python sets `__hash__` to `None` for any class that defines `__eq__` without it, and every instance becomes unhashable — the failure appears later, at the first attempt to put one in a set or dict.
- Don't write `__ne__` to mirror `__eq__`; it is derived automatically by negating `__eq__`, and a hand-written version is one more thing that can disagree with it.
- Don't assume defining `__lt__` gives you sorting *and* the other operators; sorting needs only `__lt__`, but `>` and `<=` remain unsupported unless derived or written.
- Don't compare by identity in `__eq__` (`self is other`) unless identity really is the intended equality; that is already the inherited default and needs no code.

## Checklist
- Does every class defining `__eq__` either define `__hash__` or genuinely intend to be unhashable?
- Do the values used for hashing match exactly those used for equality?
- Is any hashable instance mutated after creation?
- Do comparison methods return `NotImplemented` for operand types they do not handle?

## Notes
Equality and hashing are one contract, not two features: a dict finds a key by hashing to a bucket and then comparing for equality inside it, so an object whose hash disagrees with its equality is invisible to the lookup that should find it. That coupling is why defining `__eq__` alone deliberately disables hashing — the interpreter would rather make the object unusable in a set than let it be silently unfindable. The ordering operators carry no such constraint, which is why a decorator can safely derive them from one.
