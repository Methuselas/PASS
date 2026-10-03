---
object_id: PAT_read_a_functions_interface_with_inspect_not_its_code_object
object_type: pattern
name: Read a Function's Interface with inspect, Not Its Code Object
library_path:
- software-engineering
- languages
- python
- functions
stage_binding: 3 rough
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- functions
- introspection
- inspect
cross_links:
- rel: related_to
  target_object_id: PAT_annotate_functions_with_types_that_tools_check_not_the_interpreter
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Read a Function's Interface with inspect, Not Its Code Object

## Pattern Rule
**IF** code must discover another function's interface while running — a wrapper forwarding or validating arguments, a framework dispatching by parameter name, a tool reporting what it was handed
**THEN** ask the `inspect` module for the function's signature, which reports each parameter with its kind, default, and annotation in one object
**ELSE** when all that is needed is the function's identity, read its own attributes directly: the name attribute for messages and logs, the docstring attribute for its documentation

## Do
- Take each parameter's kind from the signature as well as its name, since positional-or-keyword, keyword-only, variable-positional, and variable-keyword are exactly the distinctions argument-forwarding code has to respect.
- Get defaults and annotations from the same signature object, so one query answers every question about the interface rather than three unrelated lookups.
- Use the function's own name attribute when a wrapper reports which function it is calling; that is what tracing and logging wrappers need and all they need.
- Treat the function's code object as an implementation detail, to be read only for something no documented inspection tool exposes.

## Don't
- Don't rebuild a parameter list from a code object's argument counts and variable-name tuple; that tuple mixes parameters with the function's other locals, says nothing about how each parameter may be passed, and has changed shape across releases.
- Don't assume parameter names discovered this way are a stable contract; an author who renames a parameter breaks anything that bound to the old name, which is why some functions deliberately mark parameters positional-only.
- Don't introspect where an argument would do; asking the caller to pass what the function needs is simpler and more robust than deducing it from a signature.
- Don't let signature inspection silently accept a callable it cannot describe; some builtins and C-implemented callables do not expose a signature, and code that assumes otherwise fails on them.

## Checklist
- Does the code need parameter kinds, not just names, and is it reading them from the signature?
- Are defaults and annotations being read through the same inspection object rather than scraped from separate attributes?
- Would passing an explicit argument remove the need to inspect anything?
- What happens when the inspected object is a builtin that cannot report a signature?

## Notes
A function carries two layers of self-description: an internal one aimed at the interpreter, holding compiled details such as local-variable names and argument counts, and a documented one aimed at programs, which reports the interface as a structured object. Early tool code reached into the first layer because it was what existed; the second is what current code should ask, because it answers the question actually being posed — how may this function be called — rather than requiring that question be reconstructed from compilation artifacts.
