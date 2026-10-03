---
object_id: PAT_define_bool_when_emptiness_is_not_falsity
object_type: pattern
name: Define __bool__ When Emptiness Is Not Falsity
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
- truthiness
- protocols
cross_links:
- rel: related_to
  target_object_id: PAT_use_or_to_pick_the_first_truthy_value_or_a_default
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Define __bool__ When Emptiness Is Not Falsity

## Pattern Rule
**IF** instances of a class appear in a truth test — `if obj:`, `while obj:`, `not obj`, or a boolean operator
**THEN** define `__bool__` to return the intended `True` or `False` whenever the default would be wrong, which it is for any class that defines `__len__` but whose emptiness should not mean falsity
**ELSE** when the class is a container and empty genuinely means false, define `__len__` alone and let truth testing fall back to it

## Do
- Define `__bool__` explicitly on a class that has `__len__` but is not "false when empty" — a response object with zero rows, a result wrapper, a form with no fields — so `if result:` cannot be read as "did this succeed".
- Let `__len__` carry truthiness for genuine collections, where empty-means-false is exactly what a reader expects.
- Return an actual `bool` from `__bool__`; the method is required to, and anything else raises `TypeError`.
- Write the explicit test (`if obj is not None:`, `if len(rows) > 0:`) at call sites where the intent is existence or emptiness specifically, rather than relying on whichever meaning the object happens to have.

## Don't
- Don't leave truthiness to inheritance by accident. Adding `__len__` to a class silently changes what `if obj:` means for every existing caller, from "I have an object" to "my object is non-empty".
- Don't define `__bool__` to mean "is valid" or "succeeded" on a type that also looks like a container; two plausible meanings for one test is worse than requiring callers to be explicit.
- Don't expect a class with neither method to ever be falsy — without `__bool__` or `__len__`, every instance is true, including ones your code considers empty or failed.
- Don't make `__bool__` expensive or side-effecting; truth tests appear in conditions that readers assume are free.

## Checklist
- Does this class define `__len__` without having considered what `if obj:` will now mean?
- For a class where emptiness and validity differ, is `__bool__` defined explicitly?
- Does `__bool__` return a real `bool` and nothing else?
- Would an explicit comparison at the call site say what is meant more clearly than relying on truthiness?

## Notes
A truth test asks `__bool__` first, falls back to `__len__` being non-zero, and treats the object as true if neither exists. The default being true is what makes the fallback dangerous rather than merely surprising: a class is true until the day someone adds `__len__` for an unrelated reason, at which point every bare `if obj:` in the codebase changes meaning with no error and no diff at the call sites.
