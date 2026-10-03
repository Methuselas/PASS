---
object_id: PAT_subclass_a_builtin_type_or_wrap_it_by_what_must_change
object_type: pattern
name: Subclass a Built-in Type or Wrap It by What Must Change
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
- builtins
- collections
cross_links:
- rel: related_to
  target_object_id: PAT_redefine_the_dunder_methods_a_wrapper_must_forward
- rel: related_to
  target_object_id: PAT_make_a_class_iterable_and_decide_how_many_scans_it_supports
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Subclass a Built-in Type or Wrap It by What Must Change

## Pattern Rule
**IF** a type is needed that behaves like a `list`, `dict`, `str` or other built-in but with added or altered behavior
**THEN** subclass the built-in only when you are *adding* methods and the inherited behavior should stay exactly as it is; when you need to *change* an existing operation so every other operation respects the change, subclass `collections.UserList`, `UserDict` or `UserString` instead, or wrap the object and expose only what you mean to support
**ELSE** when the goal is for your own class to be accepted wherever a container is expected, implement the protocol methods and register against the matching `collections.abc` type rather than inheriting any concrete built-in

## Do
- Subclass the built-in freely for pure additions — extra methods, extra attributes — where you do not override anything the type already implements.
- Reach for `collections.UserDict` or `UserList` when overriding core operations, because those classes are written in Python over a plain attribute and genuinely route their other methods through your overrides.
- Wrap rather than inherit when the new type should expose *less* than the built-in: a subclass carries every inherited method, including ones that would violate your invariants.
- Inherit from the `collections.abc` base that matches the role (`Mapping`, `MutableSequence`, `Set`) when you want the mixin methods derived from a few required ones, plus `isinstance` compatibility.
- Call the superclass implementation from an override — `super().__getitem__(i)` — rather than reaching into the underlying storage, so the inherited machinery stays consistent.

## Don't
- Don't assume a built-in's other methods honor your override. `dict.update`, `dict.get` and friends are implemented in C against the internal storage and never call your `__setitem__`, so a subclass that validates in `__setitem__` is silently bypassed by `update`.
- Don't subclass a built-in to *restrict* it; an immutable-looking subclass of `list` still inherits `append`, `extend` and the rest, and nothing stops a caller using them.
- Don't change the meaning of a core operation on a built-in subclass without expecting confusion — a `list` subclass whose indexing starts at one is still a `list` to every function that receives it.
- Don't rely on `isinstance(x, MyType)` to tell you how an object behaves; code that accepts a plain `dict` will not accept your wrapper unless it participates in the same protocol.

## Checklist
- Does this subclass override any method the built-in already defines? If so, are the type's other operations still consistent with the override?
- Would `UserDict`/`UserList` or a `collections.abc` base express this better than inheriting the concrete type?
- Does the new type inherit any operation that could break its invariants?
- Is `super()` used to reach the inherited implementation rather than bypassing it?

## Notes
Built-in types are implemented in C against their own storage, which is why inheriting from one gives you its speed but not its cooperation: the inherited methods were never written to dispatch back through a subclass's overrides. The `collections` `User*` classes exist precisely to trade that speed for cooperation — they hold a real built-in in an attribute and implement everything in Python on top of it, so one override propagates. Choosing between them is therefore not a style question but a question of whether anything you override has to be respected by anything you inherit.
