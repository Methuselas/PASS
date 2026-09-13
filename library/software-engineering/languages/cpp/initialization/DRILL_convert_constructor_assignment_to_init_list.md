---
object_id: DRILL_convert_constructor_assignment_to_init_list
object_type: drill
name: Convert Constructor Body Assignments to an Initializer List
target_skill: Using the member initialization list in declaration order instead of body assignment
library_path:
- software-engineering
- languages
- cpp
- initialization
stage_binding: 3 rough
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- initialization
- constructors
- member_initialization
cross_links:
- rel: related_to
  target_object_id: PAT_initialize_members_with_init_list
reference:
  source_title: 'Effective C++, Third Edition: 55 Specific Ways to Improve Your Programs and Designs'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Convert Constructor Body Assignments to an Initializer List

## Practice Task
Start from an `ABEntry` with two constructors — one taking a name, an address, and a phone list, and one taking nothing — whose bodies assign `theName`, `theAddress`, `thePhones`, and `numTimesConsulted`, and rewrite them to initialize those members properly.

## Target Skill
Moving member setup out of the constructor body and into default member initializers and the initialization list, in declaration order, including members that must be initialized there.

## Setup
Give the class-type members a type that counts its default constructions, copies, and assignments.

## Instructions
- Count the default constructions, copies, and assignments per class-type member that the body-assignment form performs.
- Move each per-constructor value from a body assignment into the member initialization list, and count again.
- Identify the members that gain nothing from the move.
- Put the default both constructors share on the member's declaration, and confirm each constructor produces it.
- Order the list to match the order the members are declared in the class, checking it against the class declaration rather than against itself.
- Add a member whose initializer reads another member declared after it, build at your highest warning level, and record the warnings and the value it receives.
- Add a `const` or reference member to the class, compile the body-assignment form, and record the error; then confirm it compiles when initialized through the list.

## Success Check
- The redundant work is counted, not asserted: the body-assignment form default-constructs each class-type member and then assigns it, two operations where the list performs one copy. Asserting that the list is more efficient, without saying what is avoided, restates what everyone already believes.
- The members that gain nothing are identified as well, so the run separates what this fixes from what it merely tidies.
- The shared default sits on the member's declaration, and the constructor that never mentions it is shown producing it. Repeating the default in every constructor's list passes every other bullet and leaves the next constructor free to forget it.
- The list order is checked against the class declaration rather than against itself. Members initialize in declaration order whatever the list says, so a reordered list is a statement that is not true and may draw no warning.
- The out-of-order read is built and its result recorded, including whether any warning appeared. A correct-looking list quietly reads a member that has not been initialized yet, and a clean build is not evidence against it.
- A const or reference member is actually added and the body-assignment form shown failing to compile, with the error recorded. This is the case that turns a preference into a rule.

## Common Failures
- Leaving a built-in member such as `numTimesConsulted` uninitialized in one constructor and then reading it.
- Assuming the order written in the list, rather than the declaration order, drives initialization.
- Repeating a shared default in every constructor's list instead of placing it on the declaration.

## Notes
This makes the assignment-versus-initialization distinction concrete: the body-assignment version default-constructs the string and list members before overwriting them, work the initialization list skips. A default shared by every constructor belongs on the member's declaration, where a new constructor cannot forget it. The added `const`/reference member shows the case where the list is not merely better but mandatory.
