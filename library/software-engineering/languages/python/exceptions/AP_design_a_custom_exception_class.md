---
object_id: AP_design_a_custom_exception_class
object_type: ap
name: Design a Custom Exception Class
library_path:
- software-engineering
- languages
- python
- exceptions
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: AP_decide_how_to_signal_and_handle_an_error
tags:
- python
- exceptions
- class-design
- decision-process
cross_links:
- rel: supports
  target_object_id: PAT_give_a_librarys_exceptions_a_common_category_superclass
- rel: supports
  target_object_id: PAT_inherit_user_defined_exceptions_from_exception_not_baseexception
- rel: supports
  target_object_id: PAT_add_a_constructor_or_method_to_an_exception_class_when_args_isnt_enough
- rel: supports
  target_object_id: PAT_override_str_not_repr_for_a_custom_exception_display
- rel: related_to
  target_object_id: AP_decide_how_to_signal_and_handle_an_error
reference:
  source_title: PASS software-engineering canonical synthesis
  author: Multiple accepted Python sources
confidence: high
references: []
variants: []
---

# Design a Custom Exception Class

## Objective
Given a decision to signal a specific condition by raising an exception of your own, arrive at a class (or small family of classes) that callers can catch at the right granularity, that carries the context a handler actually needs, and that displays usefully whether caught or left to reach the default handler.

## Steps / Flow
1. **Decide the hierarchy shape before writing the specific class.** If this is one of several related conditions a module or library can raise, give the family a shared category superclass so callers can catch the whole category by one name, and so adding a new specific exception later never forces existing callers to update their `except` clauses. `PAT_give_a_librarys_exceptions_a_common_category_superclass` owns this decision. If there is genuinely only one condition with no related siblings planned, skip the category superclass and derive the one class directly.
2. **Hold the base-class invariant throughout.** Whatever shape step 1 produces — one class or a category superclass plus members — every one of them derives from `Exception`, never from `BaseException` directly. `PAT_inherit_user_defined_exceptions_from_exception_not_baseexception` owns this requirement, and it applies uniformly regardless of how many classes step 1 created.
3. **Decide whether the inherited constructor is enough.** If a handler only ever needs a message to display, the inherited constructor and its `args` tuple already cover it — add nothing. If a handler needs structured, independently addressable context (a line number and a filename, not a formatted string to parse) or needs behavior that should travel with the exception (a logging method callable from any catch site), add a custom `__init__` and the needed methods. `PAT_add_a_constructor_or_method_to_an_exception_class_when_args_isnt_enough` owns this decision, and its answer determines what state is available to the next step.
4. **Decide whether the inherited display is enough.** If the exception's default display — the constructor arguments, shown as-is — already says what a reader needs, leave it. If a custom message is needed (one that reads naturally, or that formats state step 3 added), define `__str__`, not `__repr__`; the inherited `__str__` from the exception's superclass otherwise wins over any `__repr__` you write. `PAT_override_str_not_repr_for_a_custom_exception_display` owns this mechanism.
5. **Completion check.** Raise an instance and catch it at every granularity callers are expected to use — by the specific class, and by the category superclass if one exists — and confirm each catch succeeds as intended. Print or let an instance reach the default handler and confirm the displayed message matches what step 4 intended. If step 3 added state, confirm a handler can read it directly from the caught instance rather than by parsing the display text.

## Notes
The four steps correspond to four independent questions — hierarchy placement, a fixed base-class requirement, state and behavior, and display — and a design can answer "no" to steps 3 and 4 and still be complete: most custom exceptions need nothing beyond a category placement and the inherited constructor. The order matters more than it might look: hierarchy shape is a structural decision best made before the specific class exists to avoid later migration, the base-class requirement is a constant that every class in the hierarchy must independently satisfy, and the display decision in step 4 often depends on exactly what state step 3 decided to add, which is why it comes last.
