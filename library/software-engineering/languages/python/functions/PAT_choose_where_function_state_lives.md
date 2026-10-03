---
object_id: PAT_choose_where_function_state_lives
object_type: pattern
name: Choose Where Function State Lives
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
- state
- design
cross_links:
- rel: related_to
  target_object_id: PAT_retain_per_call_state_in_a_closure_declaring_nonlocal_to_change_it
- rel: related_to
  target_object_id: PAT_avoid_global_state_inject_shared_state
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Choose Where Function State Lives

## Pattern Rule
**IF** a function must remember information between calls, since its local names are discarded on every return
**THEN** choose the holder by how many copies are needed and who may see them: a module-level name for one shared copy, a closure for private per-function copies, an attribute on the function object for per-function copies that callers may also read, and a class instance when the state arrives with several behaviours
**ELSE** when nothing actually has to persist, return the value and let the caller decide where to keep it

## Do
- Reach for a module-level name only when exactly one shared copy is correct for the whole program, and accept that every holder sees every change.
- Reach for a closure when each produced function needs its own copy and nothing outside needs to see it.
- Attach an attribute to the generated function, initialised after its `def` and updated through the function's own name, when callers should be able to read or adjust the state from outside — the counter becomes an ordinary attribute fetch.
- Reach for a class when the state comes with several operations, several attributes, inheritance, or operator overloading; explicit attribute assignment then says plainly what is remembered.
- Match the choice to the question "how many copies, and visible to whom," rather than to whichever mechanism is most familiar.

## Don't
- Don't use a module-level name for per-function state: a second call to the factory resets the single shared copy, so the function produced first silently starts reading the second one's value.
- Don't reach for a one-element list in the enclosing scope and update it through its index as a way to avoid declaring the name assignable; it works only because changing an object is not assigning a name, and it hides the intent behind an index.
- Don't build a class when the state is a single counter and nothing else; the extra structure costs more to read than it returns.
- Don't expect closure state to be inspectable from outside, or a function attribute to be private; the visibility difference between them is the main reason to pick one over the other.

## Checklist
- How many independent copies of this state does the program need: one, or one per function produced?
- Does anything outside the function need to read or set it?
- Does the state come with behaviour that would justify a class, or is it a bare value?
- If a module-level name was chosen, is one shared copy genuinely correct rather than merely convenient?

## Notes
Each option trades visibility against structure. A module-level name is the simplest and the only one that cannot provide per-function copies. A closure gives per-function copies that are entirely private. A function attribute gives per-function copies that are also readable from outside, because each call of a factory produces a new function object to hang them on. A class makes the remembered data explicit and scales to richer objects, at the cost of more machinery than a single counter deserves. Whether shared mutable state should exist at all is a separate and prior question, owned by `PAT_avoid_global_state_inject_shared_state`.
