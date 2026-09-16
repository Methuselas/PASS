---
object_id: DRILL_add_const_correctness_to_a_class
object_type: drill
name: Make a C++ Class Fully const-Correct
target_skill: Applying const across a C++ class interface, including const/non-const overloads and mutable
library_path:
- software-engineering
- languages
- cpp
- const-correctness
stage_binding: 3 rough
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- const
- member_functions
- mutable
cross_links:
- rel: related_to
  target_object_id: PAT_use_logical_constness_with_mutable
reference:
  source_title: 'Effective C++, Third Edition: 55 Specific Ways to Improve Your Programs and Designs'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Make a C++ Class Fully const-Correct

## Practice Task
Take a small mutable class — a `TextBlock` holding a `std::string`, with an `operator[]` and a `length()` — and make it const-correct.

## Target Skill
Applying const to member functions and return types, overloading on constness, using `mutable`, delegating the non-const overload to the const one, and pricing what `mutable` state costs the class.

## Setup
No special setup required.

## Instructions
- Add a `const` overload of `operator[]` returning `const char&` and a non-const overload returning `char&`.
- Implement the non-const overload in terms of the const one: `static_cast` `*this` to `const`, call the const overload, then `const_cast` the const off the returned reference. State how many copies of the bounds check and the return logic now exist.
- Write the reverse as well — a const overload calling the non-const one — compile it, record whether the compiler stops it, and say which direction is safe and why.
- Rewrite the pair as one `operator[]` whose explicit object parameter is deduced, call it on a non-const and a const object, record what each call returns and whether a write through the const one compiles, and build the same member in C++20 mode and record the result.
- Add a `length() const` that caches its result, make the cache members `mutable` so it compiles, and state what marking them `mutable` concedes.
- Make the cache safe for two threads calling `length()` on the same const object, then compile a copy and a move of the class and record the result.
- Construct a const object and compile both outcomes — a read-only member succeeding, a write through it rejected — recording the compiler's message.
- Mark every parameter and local that never changes `const`, separating the ones where this changes the interface from the ones that are only a note to the reader.

## Success Check
- A const object is constructed and both outcomes are compiled: the read-only members succeed and a write through it is rejected, with the compiler's message recorded.
- The non-const overload is implemented through the const one, and the run states the count: exactly one copy of the bounds check and the return logic exists. Two overloads that each read as short and correct is the duplication this technique removes.
- The reverse direction is compiled and recorded compiling — it needs a `const_cast` on `*this`, and nothing else stops it — and the run says why it is unsafe. The two directions are not symmetric, and the compiler will not tell them apart.
- The single-member form is built and both calls recorded: the non-const object yields a modifiable reference and the const object a const one that rejects a write, from one body with no casts. The C++20 build is recorded rejecting the form, which is why the delegation stays the spelling for a C++20 codebase rather than being replaced by it.
- The caching members are marked so the const member compiles, and the run states what that concedes: the object now changes while logically constant, which is a claim about thread safety and has to be made deliberately rather than to satisfy the compiler.
- The copy and move of the thread-safe class are compiled and their result recorded. A `mutable` `std::mutex` makes the class neither copyable nor movable; a run that adds the lock and never copies the class has changed its interface without noticing.
- Parameters and locals that never change are marked, and the run separates the ones where this changes the interface from the ones where it is only a note to the reader.

## Common Failures
- Casting in the wrong direction — the const overload calling the non-const one.
- Using a const iterator where a `const_iterator` was needed.
- Leaving a cache member non-const and then const-casting to update it, instead of declaring it `mutable`.
- Adding a `mutable` mutex for thread safety and losing the class's copy and move operations unnoticed.

## Notes
This exercises the const member-function techniques together: overloading on constness, `mutable` for logical constness, and the one-directional delegation that removes duplication. If the const version ever needs a cast on `*this` to reach the non-const one, the delegation is backwards. A `mutable` cache updated inside a const member is shared state, and making it safe has a price in the class's interface.
