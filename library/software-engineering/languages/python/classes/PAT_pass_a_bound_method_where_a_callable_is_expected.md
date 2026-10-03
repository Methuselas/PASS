---
object_id: PAT_pass_a_bound_method_where_a_callable_is_expected
object_type: pattern
name: Pass a Bound Method Where a Callable Is Expected
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
- callbacks
- callables
cross_links:
- rel: related_to
  target_object_id: PAT_choose_where_function_state_lives
- rel: related_to
  target_object_id: PAT_use_lambda_only_for_a_small_inline_expression
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Pass a Bound Method Where a Callable Is Expected

## Pattern Rule
**IF** an API wants a plain callable — an event handler, a sort key, a retry hook, a thread target — and the behavior needs access to an object's state
**THEN** pass the bound method itself, `obj.handler` with no parentheses; fetching a method through an instance produces an object that already carries both the instance and the function, and calling it later supplies `self` automatically
**ELSE** when the callable needs arguments fixed at registration time rather than at call time, wrap it with `functools.partial(obj.handler, extra)` rather than reaching for a lambda

## Do
- Register `obj.handler`, not `obj.handler()`: the first hands over a callable for later use, the second calls it now and registers whatever it returned.
- Rely on the pairing: a bound method keeps a reference to its instance, so state stored on that instance is available whenever the callback eventually fires.
- Treat bound methods as ordinary values — store them in lists and dicts, pass them to `map` or `sorted`, and call them alongside plain functions, since nothing at the call site distinguishes them.
- Inspect the pairing when debugging with `m.__self__` for the instance and `m.__func__` for the underlying function.
- Reach for a method fetched from the *class* (`Cls.method`) only when passing the instance explicitly; it is an ordinary function and gets no instance of its own.

## Don't
- Don't wrap a bound method in a lambda that just calls it (`lambda: obj.handler()`); the bound method already defers the call, so the lambda adds a frame and a layer of indirection for nothing.
- Don't assume a registered bound method is garbage-free: it keeps its instance alive for as long as the registry holds it, which is a real source of objects that never get released in long-lived callback tables.
- Don't register a bound method of an object you intend to replace; the callback keeps the original instance, not whatever the name later points to.
- Don't expect a function fetched from the class to accept an instance-less call when it declares `self`; it is a plain function, and `self` is just its first parameter waiting to be filled.

## Checklist
- Is the callback registered without parentheses?
- Does anything wrap a bound method in a lambda that adds no arguments?
- Will the registry outlive the object whose method it holds, and is that intended?
- Where a class-level function is passed instead, is an instance supplied explicitly?

## Notes
A bound method is the pairing itself: fetching `obj.m` builds a small object holding the instance and the function, and calling it dispatches to the function with the instance inserted as the first argument. That is the whole mechanism behind `self`, exposed as a value you can pass around. It also makes the class-based alternative to closures concrete — both capture state for later, but a bound method carries a whole object's worth of it, with the rest of that object's behavior still reachable.
