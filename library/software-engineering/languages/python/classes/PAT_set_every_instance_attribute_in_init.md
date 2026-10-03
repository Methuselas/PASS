---
object_id: PAT_set_every_instance_attribute_in_init
object_type: pattern
name: Set Every Instance Attribute in __init__
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
- constructors
- state
cross_links:
- rel: related_to
  target_object_id: PAT_encapsulate_related_data_together
- rel: related_to
  target_object_id: PAT_choose_a_record_type_by_how_its_fields_are_used
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Set Every Instance Attribute in __init__

## Pattern Rule
**IF** a class's instances carry per-object state
**THEN** assign every one of those attributes in `__init__`, so that an instance is fully formed the moment the class call returns and every later method can assume the attribute exists
**ELSE** when the class is a plain record with no behavior, let a `@dataclass` or `typing.NamedTuple` generate the constructor instead of hand-writing one

## Do
- Give each attribute a value in `__init__` even when the value is `None` or empty; "declared absent" is a state later methods can test, while "never assigned" is an `AttributeError` waiting at an arbitrary call site.
- Let `__init__` take the attribute's initial value as a parameter rather than requiring the caller to make a second `setup()`-style call; a two-step construction leaves a window in which the object exists but is not usable.
- Read a class's `__init__` first when learning what an instance holds — since Python declares no attributes anywhere else, the constructor is the only place the full set is visible.
- Keep `__init__` to initialization: store the arguments, derive what must be derived, and leave real work to methods the caller invokes deliberately.
- Return nothing from `__init__`; it initializes the already-created instance that Python passes in as `self`, and the class call returns that instance regardless.

## Don't
- Don't create an instance attribute for the first time in an ordinary method; the attribute then exists only after that method happens to have run, and every other method silently depends on a call order nothing enforces.
- Don't rely on callers attaching attributes from outside (`obj.extra = ...`) to complete an object. Python permits it on any instance, which is exactly why it hides the omission instead of reporting it.
- Don't put a mutable default on the class body to stand in for per-instance state (see `PAT_put_shared_state_on_the_class_and_per_object_state_on_the_instance`); one list there is shared by every instance ever made.

## Checklist
- Does every attribute any method reads through `self` get assigned in `__init__`?
- Can an instance be used correctly immediately after the class call, with no follow-up setup method?
- Is there any attribute whose existence depends on which methods were called first?

## Notes
Python has no attribute declarations: an instance attribute springs into existence the first time something assigns to it, and an instance's `__dict__` holds only what has actually been assigned. That dynamism is why the discipline matters more here than in a language that reserves slots at compile time — the constructor is the one place a reader, a type checker, and the next method can all agree on what an instance contains.
