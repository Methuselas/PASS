---
object_id: DRILL_convert_a_class_to_the_pimpl_idiom
object_type: drill
name: Convert a Class to the Pimpl Idiom
target_skill: Decoupling a class interface from its implementation with a Handle class
library_path:
- software-engineering
- languages
- cpp
- compilation-dependencies
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- compilation_dependencies
- pimpl
- refactoring
cross_links:
- rel: related_to
  target_object_id: PAT_minimize_compilation_dependencies
reference:
  source_title: 'Effective C++, Third Edition: 55 Specific Ways to Improve Your Programs and Designs'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Convert a Class to the Pimpl Idiom

## Practice Task
Given a `Person` class whose header includes date.h and address.h and stores those members directly, and whose clients copy and move it, convert it to a Handle class using the pimpl idiom without changing what clients can do with it.

## Target Skill
Replacing dependencies on definitions with dependencies on declarations by hiding data behind an implementation pointer, while keeping the class's copy and move behavior intact.

## Setup
Build it as a header, an implementation file, and at least one separate client translation unit, so what fails at the client is visible.

## Instructions
- Before converting, record which of copy construction, copy assignment, move construction, and move assignment the clients use.
- Move the data members into a forward-declared `PersonImpl` class defined in a separate file.
- Give `Person` a single `std::unique_ptr` to `PersonImpl` and forward each member function to it.
- Compile a client that creates and destroys a `Person` while no destructor is declared, and record the result. Then declare the destructor in the header, define it in the implementation file, and say why the header could not hold it.
- With only the destructor declared, copy and move a `Person` in a client and record what the compiler does. Then restore every operation the clients used, recording for each where it is declared, where it is defined, and why.
- Move from a `Person`, and record what the moved-from object's pointer holds and what a forwarded call on it would do.
- In a const member function, write to a `PersonImpl` field through the pointer and record whether it compiles. Then route the class's access to the implementation through a const-qualified accessor and compile the same write again.
- Replace definition includes in the header with forward declarations where possible, and include declaration-only headers for the types used in the interface. Justify every include that remains as declaration-only or as a type the interface uses by value, and record any you kept only because removing it broke the build.
- Change `PersonImpl`, run the build, and record what actually rebuilt.
- Name the costs the conversion adds, and state what the forwarding removed that the original class had.

## Success Check
- Every include remaining in the header is justified as declaration-only, or as a type the interface uses by value. An include kept because removing it broke the build is the coupling this drill removes, and it is recorded rather than tolerated.
- The recompilation claim is tested rather than asserted: the implementation is changed, the build is run, and what actually rebuilt is recorded. Build systems differ enough that this has to be observed on the one in use.
- The destructor is accounted for: the client build with no declared destructor is recorded failing, because a `std::unique_ptr` to an incomplete type cannot be destroyed where the compiler generates the destructor, and the run says why the definition must live in the implementation file.
- Copy and move are observed, not assumed. With only the destructor declared, moving a `Person` fails to compile: the declared destructor suppressed the moves, and the pointer member left the copies deleted. Each restored operation is declared in the header and defined in the implementation file, and the run says why a move defaulted in the header fails at the client exactly as the missing destructor did. A conversion that builds only because no client copies or moves has changed the class's interface without saying so.
- The moved-from state is recorded — the pointer is null, so any forwarded call dereferences null — and the run says whether the class documents that state or guards against it, with the reason.
- The const write is built both ways and recorded: through the pointer it compiles, because `std::unique_ptr` does not pass `const` on to `PersonImpl`, and through the const-qualified accessor it is rejected. The original class rejected that write with no help, so a conversion that never tries it has lost a guarantee without noticing.
- The costs are named — one indirection per call, one allocation per object, and a forwarding function per member to keep in step. A run concluding only that compilation coupling fell has priced one side of the trade.
- What the forwarding silently removed is stated: inlining across the boundary, and any member that used to be usable in a constant expression.

## Common Failures
- Leaving definition includes in the header that reintroduce the dependency.
- Forward-declaring a standard-library type such as string instead of including its header.
- Declaring only the destructor, which leaves the class neither copyable nor movable.
- Defaulting the move operations in the header, where the implementation type is still incomplete.
- Writing to the implementation from a const member function through the bare pointer, which compiles.

## Notes
The pimpl pointer plus forward declarations move the implementation types out of the header, so client code depends only on the interface. The price is that every special member the class offers now has to be declared in the header and defined where the implementation type is complete, a moved-from handle holds nothing to forward to, and the handle's `const` no longer reaches its data unless an accessor carries it there.
