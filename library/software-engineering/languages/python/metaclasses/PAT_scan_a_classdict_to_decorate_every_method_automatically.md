---
object_id: PAT_scan_a_classdict_to_decorate_every_method_automatically
object_type: pattern
name: Scan a Class's Namespace Dictionary to Decorate Every Method Automatically
library_path:
- software-engineering
- languages
- python
- metaclasses
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- metaclasses
- decorators
- introspection
cross_links:
- rel: related_to
  target_object_id: PAT_choose_a_class_decorator_over_a_metaclass_unless_construction_or_metaclass_methods_are_needed
- rel: related_to
  target_object_id: PAT_introspect_a_functions_code_object_to_match_arguments_by_position_or_keyword
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Scan a Class's Namespace Dictionary to Decorate Every Method Automatically

## Pattern Rule
**IF** the same function decorator should wrap every method of a class, so that no `@decorator` line needs to be written above each method by hand
**THEN** iterate the class's namespace mapping, test each entry with `type(attrval) is FunctionType` to find the methods, and rebind the matching entries to `decorator(attrval)` before the class object is finished — in a metaclass `__new__` (rebinding entries in `classdict` before calling `type.__new__`) or in a class decorator (rebinding attributes on the already-built class with `setattr`)
**ELSE** when only a specific, known subset of methods needs wrapping, decorate them individually by hand; scanning the whole namespace is overkill for a handful of named methods

## Do
- Test each namespace entry with `type(attrval) is FunctionType` to distinguish plain method functions from class data, nested classes, and other non-function attributes before decorating.
- Parameterize the scanning logic over the decorator to apply (a factory function returning the metaclass or class-decorator function), so the same scanning code can apply any function decorator, not just one hardcoded choice.
- Place the rebinding in the metaclass `__new__` when the goal is to apply it to every class that declares the metaclass, including future subclasses; place it in a class decorator when it only needs to apply to one class declaration at a time.
- Verify the result by decorating a class whose methods report a trace or timing value, and confirming every method — not just the first one tested — actually produces the wrapped behavior.

## Don't
- Don't apply this scan inside the metaclass without accounting for the fact that it runs once per class construction, including for every subclass that redeclares the metaclass; methods a subclass does not override will not be rescanned unless the subclass's own namespace is scanned too.
- Don't assume this technique supports per-method decorator arguments that differ across the methods of one class; the same decorator (and the same configuration, if the decorator takes arguments) is applied uniformly to every function found.
- Don't scan and rebind inside the per-call wrapper or any code path that runs more than once per class; the scan belongs at class construction time, exactly once.

## Checklist
- Does the scan correctly distinguish plain functions from other class-level attributes before rebinding?
- Is the decorator to apply a parameter of the scanning logic, rather than hardcoded, if more than one decorator might need this treatment?
- Is the scan placed at class-construction time (metaclass `__new__`, or class-decorator body) rather than anywhere it could run more than once per class?

## Notes
A class's namespace dictionary at construction time already holds every method as an ordinary function object, before any instance-binding machinery has touched it — which is exactly what makes a blanket type check and rebind practical: the same loop that would otherwise need one decoration line per method instead runs once per class, catching whatever functions happen to be present. The choice between doing this rebinding inside a metaclass's `__new__` or inside a class decorator's body is the same choice the general metaclass-versus-decorator decision already covers; the scanning technique itself is identical either way.
