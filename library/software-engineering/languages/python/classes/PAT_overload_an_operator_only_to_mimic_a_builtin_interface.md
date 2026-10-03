---
object_id: PAT_overload_an_operator_only_to_mimic_a_builtin_interface
object_type: pattern
name: Overload an Operator Only to Mimic a Built-in Interface
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
- operator-overloading
- interfaces
cross_links:
- rel: related_to
  target_object_id: PAT_code_to_what_an_object_can_do_not_its_type
- rel: related_to
  target_object_id: PAT_match_caller_mental_model
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Overload an Operator Only to Mimic a Built-in Interface

## Pattern Rule
**IF** deciding whether a class should implement a dunder method (`__add__`, `__getitem__`, `__len__`, …) so its instances respond to an operator or built-in operation
**THEN** do it only when the object genuinely is that kind of thing — a number, a container, a sequence — or when it must satisfy an interface some existing code already expects; otherwise give the behavior an ordinary named method
**ELSE** always implement `__repr__` (and `__str__` when a separate user-facing form is wanted) regardless, since every object benefits from being readable when printed or logged

## Do
- Overload when the operator's meaning is already obvious for this type: `+` on a vector, `[]` and `len()` on a collection, `==` on a value object.
- Overload when a function you don't control expects a built-in's interface; implementing the same operations is what lets your object be passed to it.
- Make an overloaded operator behave like the built-in version it imitates: binary operators such as `+` return a *new* object and leave both operands unchanged, exactly as they do for numbers, strings, and tuples.
- Return a new instance of your own class from an operator so the result keeps the type's behavior, and let `__init__` initialize it.
- Prefer a named method (`give_raise`, `promote`, `merge_with`) whenever the operation has no obvious operator — a reader can look up a name but must guess at a symbol.

## Don't
- Don't overload an operator to do something the built-in form never does: an in-place mutation hidden behind `*` contradicts what `*` means everywhere else, and the surprise costs more than the brevity saves.
- Don't add operator support speculatively; an unimplemented dunder simply means the operation raises, which is a clearer failure than a half-meaningful one.
- Don't expect a dunder name to be reserved or special-cased by the compiler. These are ordinary attributes found by the ordinary inheritance search; Python just knows which name to look for in which situation.
- Don't reach for operator overloading as a sign of sophistication in application code; it is mainly a tool for people building types other programmers will use.

## Checklist
- Would a reader who knows Python but not this class predict what this operator does on this object?
- Does each overloaded binary operator return a new object rather than mutating in place?
- Is there any overloaded operator whose job would be clearer as a named method?
- Does the class define `__repr__`?

## Notes
Operator overloading is a dispatch mechanism and nothing more: Python maps a fixed set of operations to a fixed set of method names, looks those names up by the normal inheritance search when an instance appears in the corresponding context, and uses whatever is returned. Nothing is supplied by default for most operations, so the question is never "what will this operator do if I ignore it" — it will raise — but "is an operator the honest way to spell this behavior."
