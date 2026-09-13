---
object_id: DRILL_make_a_function_exception_safe
object_type: drill
name: Make a Function Exception-Safe with RAII and Copy-and-Swap
target_skill: Removing leaks and corruption and choosing an exception-safety guarantee
library_path:
- software-engineering
- languages
- cpp
- exception-safety
stage_binding: 3 rough
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- exception_safety
- raii
- copy_and_swap
cross_links:
- rel: related_to
  target_object_id: PAT_offer_an_exception_safety_guarantee
reference:
  source_title: 'Effective C++, Third Edition: 55 Specific Ways to Improve Your Programs and Designs'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Make a Function Exception-Safe with RAII and Copy-and-Swap

## Practice Task
Given a `changeBackground(std::istream& imgSrc)` that manually locks a `std::mutex`, deletes the old image, increments a change counter, and constructs a new image from the stream, make it exception-safe.

## Target Skill
Removing resource leaks and data corruption, then offering the strongest guarantee the function's interface can support.

## Setup
Give the image a constructor that reads from the stream and can be made to throw partway through, using input that fails after some of it has been consumed.

## Instructions
- Demonstrate both defects separately before any fix: make constructing the new image throw, show the mutex still held by probing it from a second thread, and show the counter recording a change that did not happen.
- Replace the manual lock and unlock with `std::lock_guard` or `std::scoped_lock`, and confirm no path leaves the function without releasing — early returns included, not only the throw.
- Hold the image in a `std::unique_ptr` and replace it only after the new image is constructed; increment the counter only after the change. State the ordering as the mechanism.
- Make the image constructor throw again, and record the object's state and the stream's read position before and after the call.
- Name the guarantee actually reached, basic or strong, with the reason.
- Restructure with copy-and-swap over a pimpl, check that the swap committing the change cannot throw, and repeat the failing call.
- Identify concretely what still prevents the strong guarantee, and state the guarantee this interface can support.

## Success Check
- Both defects are demonstrated separately before any fix — the lock still held after a throw, seen from another thread, and the counter recording a change that did not happen. Naming them from reading the code is the setup rather than the result.
- The guard replaces the manual pair, and the run confirms no path leaves the function without releasing, early returns included and not only the throw.
- The ordering is stated as the mechanism: the old image is released only once the new one exists, and the counter advances only after the change, so a throw at any point leaves the earlier state intact.
- The failing call is actually run after the reordering, and both records are kept: the object is unchanged, and the stream's read position has moved. A run that records only the object reports a strong guarantee the function does not offer.
- The guarantee actually reached is named — basic or strong — with the reason, rather than assumed to be strong because the code improved. This is the bullet that separates the two halves of this exercise.
- The commit step's swap is checked as non-throwing, by a trait or a `noexcept` it can be read from, rather than taken on trust. The commit is only as safe as that swap, and nothing else in the version shows whether it can throw.
- What blocks the strong guarantee is identified concretely: input consumed from an arbitrary `std::istream` cannot be put back, so the run states the guarantee this interface can support rather than the one the implementation would prefer to claim, and notes that requiring a seekable stream would change the interface, not the implementation.

## Common Failures
- Incrementing the counter before the change has succeeded.
- Assuming copy-and-swap delivers the strong guarantee despite a non-local side effect.
- Probing the held mutex with `try_lock` from the thread that already owns it, which is undefined for `std::mutex`.

## Notes
RAII removes the leak, reordering removes the corruption, and copy-and-swap makes the object's own state transactional — but consumed stream input is a side effect outside the object, and it caps the function at the basic guarantee.
