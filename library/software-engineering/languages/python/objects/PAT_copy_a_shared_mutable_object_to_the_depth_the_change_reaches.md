---
object_id: PAT_copy_a_shared_mutable_object_to_the_depth_the_change_reaches
object_type: pattern
name: Copy a Shared Mutable Object to the Depth the Change Reaches
library_path:
- software-engineering
- languages
- python
- objects
stage_binding: 3 rough
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: PAT_make_immutability_deep
tags:
- python
- references
- aliasing
- mutability
- copying
cross_links:
- rel: related_to
  target_object_id: PAT_make_immutability_deep
- rel: related_to
  target_object_id: PAT_dont_mutate_input_parameters
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Copy a Shared Mutable Object to the Depth the Change Reaches

## Pattern Rule
**IF** Python code is about to change a list, dict, set or other mutable object in place, and that object may also be reachable through another name — a second variable, a caller's argument, a default value, an element of another container
**THEN** decide whether the other holders should see the change; if not, make a copy first, and make it as deep as the parts you will change — a shallow copy for top-level edits, `copy.deepcopy` when nested objects will be changed
**ELSE** when sharing is the intent (the caller asked you to fill their list), change the object in place and say so in the function's name or docstring.

## Do
- Remember that every assignment, argument pass, `for` target and container insertion stores a reference, never a copy: after `M = L`, `L[0] = 24` shows up in `M`.
- Make shallow copies with the type's own tools: `L[:]`, `list(L)`, `L.copy()`, `dict(D)`, `D.copy()`, `set(S)`, or `copy.copy(x)` for any object.
- Use `copy.deepcopy(x)` when the edit reaches inside nested objects; a shallow copy of `[[1], [2]]` still shares the inner lists, so appending to `copy[0]` changes the original too.
- Rebind instead of mutating when you only need a new value: `a = a + [x]` builds a new list and leaves other holders alone.
- When a surprise change appears, check sharing with `a is b` on the suspected objects before looking for other causes.

## Don't
- Don't expect rebinding a name to affect other names: `b = 'shrubbery'` after `b = a` changes only `b`. Only in-place operations on a mutable object are visible through every reference.
- Don't reach for `deepcopy` by reflex; it copies everything reachable, can be slow on large graphs, duplicates objects such as caches that were meant to stay shared, and raises `TypeError` on objects that cannot be copied, such as locks.
- Don't treat a slice or `.copy()` as a full copy of nested data.
- Don't convert an argument to a tuple at the call just to stop a function from changing it; that makes every attempted change an error rather than a private one, and it also takes away the list methods the function may legitimately want to call. Pass a copy when the caller's object must survive unchanged.
- Don't build a grid with repetition: `[[0] * 3] * 3` holds three references to one inner list, so setting `grid[0][0]` changes every row. Build each row separately with `[[0] * 3 for _ in range(3)]`.
- Don't initialize two names you need to vary independently with one chained or multiple-target assignment to a mutable literal, such as `a = b = []`; both names get the same list object, so appending through one shows up through the other. Give each its own literal (`a = []; b = []`) instead.
- Don't expect `for x in L: x += 1` to change `L`; each iteration just rebinds the loop variable `x` to a new value, the same as any other assignment. To mutate `L` itself by position, index it instead: `for i in range(len(L)): L[i] += 1`.

## Checklist
- Can the object being changed be reached from anywhere else?
- Should those other holders see this change?
- Does the change reach nested objects, and is the copy at least that deep?
- Does a function that mutates its argument say so?

## Notes
In Python a variable is a name bound to an object, not a box that holds a value. Types live with objects; names have none. Immutable objects (numbers, strings, tuples) can be shared freely because no one can change them; the hazard exists only for mutable ones, and it is pervasive because function arguments are passed by the same assignment model.

Objects are reclaimed when their reference count drops to zero, with a separate collector for reference cycles. This is why dropping every name for an object is enough to free it, and why a cache that should not keep its entries alive holds them through `weakref` references instead of ordinary ones.
