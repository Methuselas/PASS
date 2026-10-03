---
object_id: PAT_annotate_functions_with_types_that_tools_check_not_the_interpreter
object_type: pattern
name: Annotate Functions with Types That Tools Check, Not the Interpreter
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
- annotations
- type-hints
cross_links:
- rel: related_to
  target_object_id: PAT_code_to_what_an_object_can_do_not_its_type
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Annotate Functions with Types That Tools Check, Not the Interpreter

## Pattern Rule
**IF** a function's parameter and result types are worth stating where callers will read them
**THEN** write them as annotations in the header — a colon and the type after each parameter name, an arrow and the type before the colon that ends the line — understanding that the interpreter only records them while a separate checker, editor, or library is what acts on them
**ELSE** when the thing worth saying is not a type — a unit, a permitted range, a validation rule — keep it out of the annotation and put it in the docstring or an explicit check, because every current reader and tool will read an annotation as a type

## Do
- State what callers must supply and what they get back, including the return type, and let a static checker catch violations before the code runs rather than asserting them again in the body.
- Read annotations back with the standard resolution helpers rather than the raw annotations dictionary when a tool must act on them, since resolving string and forward-referenced forms is exactly what those helpers exist to do.
- Order a header as name, then annotation, then default, so an annotated parameter with a default carries both without ambiguity.
- Annotate the capability a function actually needs — an iterable of numbers rather than one concrete container class — so the annotation documents the real interface instead of narrowing it.
- Keep validating input that arrives from outside the program with real checks at that boundary; an annotation states intent and guards nothing at runtime.

## Don't
- Don't expect an annotation to be enforced: a call that passes the wrong type raises nothing by itself, and the eventual error appears wherever an unsupported operation is finally attempted, far from the call.
- Don't use an annotation slot for an arbitrary object — a descriptive string, a pair of bounds, a number — the way early examples did before conventions settled; tools now read that position as a type, so anything else misleads both them and the next reader.
- Don't try to annotate a lambda; the syntax is available only in a `def` header.
- Don't treat an annotation as a substitute for a usable interface: narrowing a parameter to one class on paper while the body only iterates it contradicts what the function really accepts.

## Checklist
- Does every annotation name a type, rather than some other fact about the parameter?
- Is the return type stated as well as the parameter types?
- Does the annotation describe the capability the body actually requires?
- Is anything that must hold at runtime still checked at runtime, independently of the annotations?

## Notes
Annotations began as a general-purpose slot that the language deliberately left without meaning, which is why the earliest examples of them attach strings and tuples as freely as types. That space has since been claimed: the convention is now firmly that an annotation is a type, read by tooling outside the interpreter, and that convention is what makes the feature useful. The interpreter's indifference remains exactly as it was, which is the one property worth keeping in mind — nothing about an annotation stops a call that contradicts it, so `PAT_code_to_what_an_object_can_do_not_its_type` still governs what the body may assume.
