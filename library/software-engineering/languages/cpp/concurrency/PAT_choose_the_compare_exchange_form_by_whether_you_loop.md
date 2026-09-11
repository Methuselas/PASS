---
object_id: PAT_choose_the_compare_exchange_form_by_whether_you_loop
object_type: pattern
name: Choose the Compare-Exchange Form by Whether You Loop
library_path:
- software-engineering
- languages
- cpp
- concurrency
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- concurrency
- atomics
- lock_free
- correctness
cross_links:
- rel: related_to
  target_object_id: PAT_check_an_atomic_is_lock_free_before_relying_on_it
- rel: related_to
  target_object_id: PAT_keep_memory_alive_until_the_compare_and_swap_completes
- rel: related_to
  target_object_id: PAT_classify_synchronization_by_progress_guarantee
- rel: related_to
  target_object_id: AP_make_shared_state_safe_in_cpp
reference:
  source_title: 'Concurrency with Modern C++: What every professional C++ programmer should know about concurrency'
  author: Rainer Grimm
confidence: high
references: []
variants: []
---

# Choose the Compare-Exchange Form by Whether You Loop

## Pattern Rule
**IF** you are writing a compare-and-exchange against an atomic — the operation underneath essentially every non-blocking algorithm
**THEN** normally take the weak form when a retry loop treats every failure alike and the strong form when one-shot semantics must distinguish mismatch from success, because only the weak form may fail spuriously
**ELSE** where you want to overwrite unconditionally and do not care what was there, an exchange is the operation you want and no comparison is involved.

## Do
- Fix what the operation does to its first argument, since this is where the misreadings start. On success the atomic takes the desired value; on failure the *expected* argument is overwritten with what the atomic actually held. That write-back is what makes a retry loop converge — the next attempt is already carrying the current value.
- Read the failure of the weak form as ordinary rather than exceptional. It exists because some processors have no single compare-exchange instruction and must synthesize one from a pair that can be disturbed between halves; a spurious failure is that disturbance, not a sign that anything is wrong.
- Prefer the weak form in a loop that already recomputes from the returned expected value and can absorb spurious failure. Use the strong form when a failed attempt has separate meaning or expensive side effects, even if an outer control structure happens to loop.
- Keep the loop body free of anything that must happen exactly once. It may run several times against an unchanged value, so any side effect inside it happens more often than the successful exchange does.

## Don't
- Don't use one weak call when the caller interprets failure as a definite value mismatch. A weak call outside a loop is valid only when spurious failure is an accepted outcome handled by the contract.
- Don't reload the expected value at the top of the loop. The failed call has already written the current value into it, so a manual reload is redundant at best and, if it reads the atomic separately, opens a window between the read and the next attempt.
- Don't assume that seeing the expected value means nothing happened in between. The value may have changed away and back, which every compare-and-exchange is blind to by construction — and which is a distinct hazard with its own remedies rather than something the choice of form addresses.

## Checklist
- Is this call inside a retry loop?
- If it is, is the weak form being used?
- If it is not, is the strong form being used?
- Does the loop body do anything that must not be repeated?
- Does the surrounding algorithm care whether the value changed away and back?

## Notes
The two forms are best matched to failure semantics rather than syntax alone. Weak compare-exchange is ideal when all failure—including a spurious one—feeds the same retry path. Strong compare-exchange is appropriate when a one-shot failure must mean the value comparison failed. Either can be used in a loop when the surrounding algorithm gives a reason.

The write-back on failure is the detail most worth carrying away, because it is what makes the idiomatic loop as short as it is. A loop that retries until the exchange succeeds needs no body at all in the simplest case: the argument it passes is updated for it each time round.

The blindness to a value that changes away and returns is inherent to comparing values rather than identities, so it is not a defect in either form and cannot be fixed by choosing between them. It becomes a problem specifically when the value is a pointer and the storage it names can be recycled, which is where the reclamation question arises.
