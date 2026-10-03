---
object_id: PAT_collect_arguments_with_stars_in_a_header_and_unpack_them_at_a_call
object_type: pattern
name: Collect Arguments with Stars in a Header and Unpack Them at a Call
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
- varargs
cross_links:
- rel: related_to
  target_object_id: PAT_pass_an_iterable_directly_instead_of_materializing_a_list_first
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Collect Arguments with Stars in a Header and Unpack Them at a Call

## Pattern Rule
**IF** writing a function that must accept however many arguments callers choose to pass, or a call that must pass arguments assembled at runtime
**THEN** use the star forms in the matching position: `*name` and `**name` in a header collect the extra positional and named arguments into a tuple and a dict, while `*iterable` and `**mapping` at a call spread a collection back out into individual arguments
**ELSE** when the argument list is known and fixed, name the parameters explicitly; star forms buy flexibility a fixed signature does not need, at the cost of a signature that says less about what the function wants

## Do
- Collect extra positional arguments with `*name`, which arrives as an ordinary tuple, and extra named ones with `**name`, which arrives as an ordinary dict, then process them with normal tuple and dict tools.
- Spread a runtime-assembled collection into a call with `*values` or `**options` so the number of arguments does not have to be known when the code is written.
- Forward both collections unchanged when writing a wrapper: collect with `def wrapper(func, *pargs, **kargs)` and pass along with `func(*pargs, **kargs)`, the shape every tracer, timer, and generic dispatcher uses.
- Expect the star at a call to accept any iterable, not only a tuple or list; an open file spreads its lines into individual arguments the same way a tuple spreads its items.
- Keep the header order: ordinary parameters, then defaulted ones, then `*name`, then any keyword-only names, then `**name` last; a different order is a syntax error rather than something resolved at call time.

## Don't
- Don't confuse the two directions: one star in a header gathers positional arguments while one star at a call spreads them, and the same inversion holds for two stars and named arguments.
- Don't expect a `*name` parameter to stay lazy because the call accepted an iterable; a header always bundles what it collects into a tuple, which materialises whatever was passed.
- Don't reach for star forms to avoid naming parameters the function actually requires; a signature that collects everything tells neither a reader nor a checker what the function needs.
- Don't place `**name` anywhere but last in a header or a call; everything else may move, but the arbitrary-keywords form may not.

## Checklist
- Does the function genuinely accept an unpredictable number of arguments, or is a fixed signature being avoided out of habit?
- At a forwarding call, are both collections passed along with stars rather than as a tuple and dict in single parameters?
- Does the header list its forms in the required order, with the double-star form last?
- Where a call spreads an iterable, is materialising it into a tuple acceptable at that point?

## Notes
The symmetry is the thing worth holding on to: the same two tokens mean "gather the rest here" where parameters are declared and "spread this out" where arguments are supplied. Because the call side accepts any iterable, it composes with everything that produces values lazily, which is the broader habit `PAT_pass_an_iterable_directly_instead_of_materializing_a_list_first` describes — with the one caveat that a collecting header is the point where laziness ends.
