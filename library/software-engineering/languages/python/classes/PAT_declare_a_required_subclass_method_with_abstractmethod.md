---
object_id: PAT_declare_a_required_subclass_method_with_abstractmethod
object_type: pattern
name: Declare a Required Subclass Method with abstractmethod
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
- inheritance
- abstract-base-class
cross_links:
- rel: related_to
  target_object_id: PAT_extend_a_superclass_method_by_calling_it_through_super
- rel: related_to
  target_object_id: PAT_code_to_what_an_object_can_do_not_its_type
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Declare a Required Subclass Method with abstractmethod

## Pattern Rule
**IF** a superclass calls a method it deliberately does not implement, expecting every concrete subclass to supply it
**THEN** derive the superclass from `abc.ABC` and mark the hook `@abstractmethod`, so that instantiating any class that has not implemented it fails immediately with a `TypeError` naming the missing method
**ELSE** when the hook has a sensible default behavior, implement that default instead of marking it abstract — a method subclasses *may* override is not the same as one they *must*

## Do
- Write `class Base(abc.ABC):` and decorate each required hook with `@abstractmethod`; a subclass becomes instantiable only once every abstract method has an implementation.
- Keep the abstract method's body empty (`...` or a docstring); it exists to declare the interface, and nothing should call it.
- Let the superclass's concrete methods call the hook through `self`, which is what makes the subclass's implementation the one that runs: every `self.attr` starts a fresh search from the instance, so it finds the lowest definition.
- Reach for `typing.Protocol` instead when the requirement is structural — any object with these methods will do, and callers should not have to inherit from anything.
- Raise `NotImplementedError` from a stub only where `abc` is not an option, such as a base class you do not control, and accept that the error then arrives at first call rather than at construction.

## Don't
- Don't signal the requirement with `assert False, "must be defined"`. Assertions are stripped entirely when Python runs with `-O`, so the guard silently disappears in exactly the optimized runs where a missing override would be hardest to diagnose.
- Don't leave the hook undefined altogether and rely on the resulting `AttributeError`. The failure then names an attribute lookup deep inside the superclass rather than the contract the subclass broke, and only when that code path finally runs.
- Don't mark a method abstract to document an *optional* extension point; doing so forces every subclass to write a method it does not need.
- Don't expect the abstract declaration to check the signature. Python verifies only that the name is defined somewhere lower in the tree, not that it takes compatible arguments.

## Checklist
- Does every method the superclass calls but does not implement carry `@abstractmethod` on an `abc.ABC` base?
- Does any required-override stub still use a bare `assert` that `-O` would remove?
- Would a `Protocol` express this better, given that callers may not want to inherit?
- Is each abstract method genuinely required, rather than an optional hook with a reasonable default?

## Notes
This is the template-method shape: the superclass owns the overall flow and delegates the varying step to a method the subclass fills in. It works because attribute lookup restarts at the instance on every `self.` reference, so a call made from superclass code still lands on the subclass's override. What `abc` adds is only the timing of the error — the mechanism works without it, but the failure then appears at the call site instead of the construction site, which is usually much further from the mistake.
