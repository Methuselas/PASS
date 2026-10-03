---
object_id: PAT_introspect_a_functions_code_object_to_match_arguments_by_position_or_keyword
object_type: pattern
name: Introspect a Function's Code Object to Match Arguments by Position or Keyword
library_path:
- software-engineering
- languages
- python
- decorators
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- decorators
- introspection
- arguments
cross_links:
- rel: related_to
  target_object_id: PAT_use_nested_functions_not_callable_classes_for_decorators_that_wrap_methods
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Introspect a Function's Code Object to Match Arguments by Position or Keyword

## Pattern Rule
**IF** a decorator or other generic tool must process specific named arguments of a wrapped function regardless of whether a caller passes them positionally or by keyword, including arguments a caller may omit to accept a default
**THEN** read the function's expected parameter names from its code object (`func.__code__.co_varnames[:func.__code__.co_argcount]`), slice that list to the number of positional arguments actually received to find which names arrived positionally, and check the rest against the keyword-arguments dictionary
**ELSE** when the tool can require one fixed calling convention (always by position, or always by keyword), skip introspection entirely; matching by convention alone is simpler and sufficient

## Do
- Fetch the parameter-name list once per decoration (outside the per-call wrapper), since it depends only on the function, not on any particular call.
- Slice `expected[:len(args_received_positionally)]` to get the subset of names that correspond to this call's actual positional arguments; those names are positional here regardless of what the function's signature allows elsewhere.
- Check a to-be-processed name against the keyword dictionary first, then against the sliced positional-names list, and treat a name found in neither as omitted and defaulted — in that order, since a name cannot be both passed by keyword and present in the positional slice for the same call.
- Rely on the two ordering guarantees Python's own call and definition syntax already enforce — all positional arguments precede all keyword arguments at a call, and all non-default parameters precede all default parameters in a definition — rather than re-deriving them.

## Don't
- Don't try to fully re-implement Python's own argument-matching algorithm to validate whether a call is well-formed before running it; let an actually invalid call fail naturally when the wrapper invokes the real function, and limit introspection to locating the arguments the tool itself needs to check.
- Don't assume this technique covers arbitrary `*args` positions a caller supplies beyond the function's named parameters; names collected by a `*args`-style catch-all parameter have no fixed position to map a decorator's by-name configuration back to.
- Don't forget that nested decorators change the wrapper's own call signature; a decorator applied outside another one sees the inner wrapper's generic `*args, **kwargs` shape, not the original function's named parameters, so position-based matching degrades to keyword-only matching at that outer layer.

## Checklist
- Does the tool fetch expected parameter names from `__code__` once per decoration, rather than once per call?
- Is a name's positional-or-keyword status determined by checking the keyword dictionary and the sliced positional-names list, in that order?
- Where the decorator may be nested with others, has the resulting keyword-only degradation at outer layers been accounted for or accepted?

## Notes
The technique works because of two ordering rules Python's own syntax already guarantees rather than anything the tool has to enforce itself: positionals always precede keywords in a call, and required parameters always precede defaulted ones in a definition. Those two guarantees are what let a slice of the expected-names list, taken to the length of the positional arguments actually received, reliably identify which parameter each positional argument filled — without the tool ever having to simulate the full argument-binding process Python itself performs at call time.
