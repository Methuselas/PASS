---
object_id: PAT_test_for_a_missing_value_with_is_none_not_truthiness
object_type: pattern
name: Test for a Missing Value With is None, Not Truthiness
library_path:
- software-engineering
- languages
- python
- expressions
stage_binding: 3 rough
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- none
- truthiness
- defaults
- conditional_expressions
cross_links:
- rel: related_to
  target_object_id: PAT_write_boolean_expressions_to_be_read_not_decoded
reference:
  source_title: 'Beyond the Basic Stuff with Python: Best Practices for Writing Clean Code'
  author: Al Sweigart
confidence: high
references: []
variants: []
---

# Test for a Missing Value With is None, Not Truthiness

## Pattern Rule
**IF** you are deciding whether an optional value was supplied, or choosing a fallback for it, and `0`, `""`, `False` or an empty collection is a legitimate value
**THEN** test for `None` by identity and choose the fallback explicitly, because truthiness, `or` and `and … or` treat every falsy value as missing.

## Do
- Write a fallback as `timeout = 30 if timeout is None else timeout`. The shorter `timeout = timeout or 30` returns 30 when a caller deliberately passes `0`, and `name or "anonymous"` discards a deliberate `""` the same way.
- Choose between two values with `a if cond else b`. The older `cond and a or b` returns `b` whenever `a` is falsy even though `cond` is true — with `cond=True, a=0` it yields the fallback.
- Compare with `is None`, never `== None`. `==` asks the other object's `__eq__`, which can answer True: an object whose `__eq__` always returns True makes `x == None` True while `x is None` stays False. There is exactly one `None`, so identity is the precise test.
- Keep bare `if value:` for a genuine boolean, and for a collection where empty and absent really are handled the same way; there the truthiness reading is the intended one.

## Don't
- Don't write `flag is True` or `flag == True`. `is True` is False for `1` and for every truthy value that is not the `bool` singleton, and nothing warns about it; test a boolean bare, as `if flag:`.
- Don't trust a fallback because the tests pass. `x or default` is right for every value except the falsy ones, so the defect waits for the first caller who legitimately passes `0`, `""` or an empty list.

## Checklist
- Can this optional value legitimately be `0`, `""`, `False` or empty? If so, is every presence test written `is None` or `is not None`?
- Is any fallback still written `x or default`, or any choice `cond and a or b`, where the chosen value can be falsy?
- Does any comparison with `None` use `==` or `!=`?

## Notes
The trap is that Python gives almost every type a truth value, so a presence test written as truthiness type-checks, reads naturally, and is right for the typical input. What it actually asks is whether the value is falsy, and `None` is only one of the falsy values; `0`, `0.0`, `""`, `[]`, `{}` and `False` answer the same way. The conditional expression exists partly because the `and … or` idiom had exactly this defect and was widely used anyway.

Behaviour quoted here was checked on CPython 3.14.7, identically on the default and free-threaded builds.
