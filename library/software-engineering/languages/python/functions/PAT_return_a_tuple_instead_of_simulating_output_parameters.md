---
object_id: PAT_return_a_tuple_instead_of_simulating_output_parameters
object_type: pattern
name: Return a Tuple Instead of Simulating Output Parameters
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
- return-values
- arguments
cross_links:
- rel: related_to
  target_object_id: PAT_unpack_or_swap_values_with_sequence_assignment
- rel: related_to
  target_object_id: PAT_dont_mutate_input_parameters
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Return a Tuple Instead of Simulating Output Parameters

## Pattern Rule
**IF** a function must hand the caller back more than one value, or hand back an updated version of something it was given
**THEN** return the values as a tuple, whose parentheses are optional, and let the caller unpack them into names at the call site, rather than changing the arguments in place to communicate results
**ELSE** when changing the caller's object really is the function's advertised job, change it and say so in the function's name and documentation instead of also returning it

## Do
- Write `return first, second` and receive with a matching unpacking assignment, so the names that change at the caller are visible on the line that calls the function.
- Treat the returned tuple as the normal way to give back several results; building a tuple costs nothing extra and needs no container type decided in advance.
- Return a fresh object rather than editing the caller's when the function's job is to compute a result, so a caller that still needs the original keeps it.
- Let a function whose entire purpose is an in-place change return nothing, so no caller is tempted to assign the result of a call that has already done its work.

## Don't
- Don't use argument mutation as a back channel for results the caller is expected to read afterwards; nothing at the call site shows that a name's value changed, so the next reader has to find the function and check.
- Don't both change an argument in place and return it; callers then cannot tell from a call whether they hold a new object or the one they passed in.
- Don't expect rebinding a parameter name inside the function to reach the caller at all; that assignment affects only the function's own local name.
- Don't wrap results in a list or dict when a tuple would do, unless callers need to grow or look the results up by name.

## Checklist
- Does each result this function produces leave through its return value rather than through a changed argument?
- At the call site, is it visible which names the call updates?
- If the function does change a passed-in object, does its name say so?
- Does any function both change an argument and return it?

## Notes
Python has no call-by-reference, so the effect other languages get from output parameters is obtained here by returning a tuple and unpacking it, which makes the update explicit at both ends — the function says what it produces, and the call says what it rebinds. The receiving half is `PAT_unpack_or_swap_values_with_sequence_assignment`; the design rule about leaving a caller's object alone is `PAT_dont_mutate_input_parameters`. This card is the Python mechanism that lets both hold at once.
