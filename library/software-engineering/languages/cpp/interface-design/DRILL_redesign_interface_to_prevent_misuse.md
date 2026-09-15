---
object_id: DRILL_redesign_interface_to_prevent_misuse
object_type: drill
name: Redesign an Error-Prone Interface So Misuse Won't Compile
target_skill: Using types, value constraints, and ownership to make an interface hard to misuse
library_path:
- software-engineering
- languages
- cpp
- interface-design
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- interface_design
- type_safety
- hard_to_misuse
cross_links:
- rel: related_to
  target_object_id: PAT_make_interfaces_hard_to_misuse
reference:
  source_title: 'Effective C++, Third Edition: 55 Specific Ways to Improve Your Programs and Designs'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Redesign an Error-Prone Interface So Misuse Won't Compile

## Practice Task
Given a `Date(int month, int day, int year)` constructor, redesign it so wrong-order and out-of-range arguments cannot compile.

## Target Skill
Preventing client mistakes with distinct types, constrained values, and removed bookkeeping.

## Setup
No special setup required.

## Instructions
- List the client mistakes the current signature allows — swapped month/day, and out-of-range values — writing each as a call that compiles today.
- Introduce distinct Day, Month, and Year types three ways — with converting constructors, as aggregates, and with `explicit` constructors — and against each, compile both the raw transposed call and a wrong-order call with each argument in its own braces, such as `Date({30}, {3}, {1995})`, recording which compile. Keep the form that rejects both.
- Before constraining Month to its valid values, try the scoped-enumeration version: record whether it fixes the argument order and refuses a plain integer, then cast an out-of-range integer to it and record what the result holds.
- Constrain Month to its valid values using predefined Month objects rather than a raw int or an enumeration of either kind.
- Exercise the final design both ways — the wrong call failing to compile with the rejection recorded, the right call succeeding.
- Attempt to construct an invalid month and show it impossible rather than merely inconvenient, saying whether what you built rejects at compile time or validates at run time.
- Build the same attempt with C++20's calendar types: construct a `std::chrono::month` from 13 and try to pass a plain integer where a month is expected, recording what compiles and what the month reports. State which approach this interface should use, with the reason.
- State whether a factory for this type should return a smart pointer, with the reason.
- State what the redesign costs.

## Success Check
- The mistakes the original signature permits are listed before the redesign, each written as a call that compiles today.
- The three wrapper forms are compiled against both calls and the results recorded: converting constructors let the raw transposed call through, aggregates refuse the raw call and accept the wrong-order call with each argument in its own braces, and only `explicit` constructors reject both. A run that tests only the raw call, or braces the whole argument list instead of each argument, can settle on aggregates and still accept the transposition.
- The scoped-enumeration attempt is made first and the point where it stops is recorded: it fixes the ordering and refuses implicit conversion, and an explicit cast still yields a value nobody declared. Skipping to the answer removes the reason the answer is what it is.
- The final design is exercised both ways — the wrong call fails to compile, the right call succeeds — with the compiler's rejection recorded rather than predicted.
- Constructing an invalid month is attempted, with the compiler's rejection recorded, and shown impossible rather than merely made inconvenient. A constructor validating at run time is a different technique, and the run says which of the two was built.
- The standard's calendar types are exercised, not cited: `std::chrono::month{13}` compiles and reports `ok() == false`, and a plain integer does not convert to a month implicitly. The run chooses between that design and an unconstructible Month with the reason, rather than treating the standard's choice as a defect or leaving it out.
- The factory answer rests on whether there is a release obligation to remove: a small value type returned by value has none, so a smart pointer would add an allocation and remove nothing.
- The cost is stated: more types to declare, longer call sites, and conversions at every boundary where these values arrive as plain integers anyway.

## Common Failures
- Using an unscoped enum for the month, whose enumerators leak into the surrounding scope and
  convert implicitly to int, instead of a constrained type.
- Stopping at a scoped enumeration and reporting the interface closed. It is a real improvement and
  the implicit-conversion objection does not apply to it — see
  `PAT_prefer_the_form_that_refuses_what_you_did_not_mean`, which asks for exactly this form
  elsewhere. What it does not do is make an invalid value unconstructible, because a cast still
  reaches one. Only a type whose constructor is private and whose valid values are the only ones
  handed out closes that.
- Leaving the argument order unenforced so a swap still compiles.
- Wrapping the values in aggregates, which refuse the raw call and accept a wrong-order call with each argument in its own braces.

## Notes
The type system is the tool that turns runtime mistakes into compile errors, and consistency plus removed bookkeeping do the rest. Wrapper types do that job only when their constructors are explicit.
