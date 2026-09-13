---
object_id: DRILL_fix_templatized_base_class_name_access
object_type: drill
name: Fix Access to a Name in a Templatized Base Class
target_skill: Enabling name lookup into a templatized base with this->, using, or qualification
library_path:
- software-engineering
- languages
- cpp
- templates
stage_binding: 3 rough
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- templates
- inheritance
- name_lookup
cross_links:
- rel: related_to
  target_object_id: PAT_access_templatized_base_members_explicitly
reference:
  source_title: 'Effective C++, Third Edition: 55 Specific Ways to Improve Your Programs and Designs'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Fix Access to a Name in a Templatized Base Class

## Practice Task
Given a derived class template (a LoggingMsgSender) that calls an inherited virtual function (sendClear) from its base class template (MsgSender) and won't compile, make it compile three different ways and establish what each way does at run time.

## Target Skill
Turning on the compiler's search of a templatized base class for an inherited name, and choosing the form that keeps virtual dispatch.

## Setup
Build in the compiler's standards-conforming mode.

## Instructions
- Reproduce the failure: compile the unqualified call to the inherited function, and record the compiler's message.
- Declare a namespace-scope function with the same name before the templates, compile the unqualified call again, run it, and record which function it called. Then remove that function.
- Fix it with a this-> prefix on the call, and compile it.
- Fix it again with a using declaration bringing the base name into the derived scope, and compile it.
- Fix it a third time with explicit base-class qualification, and compile it.
- Override the inherited function in a class derived from the fixed template, call through each of the three fixes, and record which version each one runs.
- Add a base specialization that omits the name. Compile the template beside it without instantiating the derived template for that specialization, then instantiate it, and record where the error arrives.
- Rank the three fixes with the condition that selects each.

## Success Check
- The failure is reproduced first and the compiler's message recorded, because that message is what a reader actually meets and it does not plainly describe the cause. A compiler in a permissive mode can accept the unqualified call, so a run that could not reproduce the failure has tested its build settings, not the rule.
- The unqualified call is rebuilt beside a namespace-scope function of the same name, and recorded compiling and calling that function rather than the base member. That missing error is the dangerous case: a run that meets only the refusal learns to trust any unqualified call that builds.
- All three fixes are compiled rather than one compiled and two described.
- Dispatch is observed, not stated: `this->` and the using declaration run the override, and explicit qualification runs the base version. The run says why that makes qualification the worst default for a virtual function, rather than listing it as a third option of equal standing.
- The missing specialization is built both ways: the template compiles beside a specialization that omits the name, and the error arrives only when the derived template is instantiated with it. That timing is the substance of the exercise.
- The three are ranked with the condition that selects each, so the run ends in a choice rather than an inventory.

## Common Failures
- Leaving the call unqualified and expecting inheritance to just work across the template boundary.
- Using explicit qualification on a virtual function and silently disabling virtual dispatch.
- Reproducing the failure under a permissive compiler mode, where the unqualified call compiles.
- Trusting a clean build of an unqualified call that bound to a same-named function outside the class.

## Notes
All three fixes promise the name is inherited; C++ diagnoses an unfounded promise later, when the template is instantiated with a base specialization that lacks it. An unqualified call makes no such promise, so it either fails or quietly finds something else. Only explicit qualification also changes which function runs.
