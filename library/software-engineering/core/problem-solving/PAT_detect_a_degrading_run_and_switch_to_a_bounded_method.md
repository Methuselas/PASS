---
object_id: PAT_detect_a_degrading_run_and_switch_to_a_bounded_method
object_type: pattern
name: Detect a Degrading Run and Switch to a Bounded Method
library_path:
- software-engineering
- core
- problem-solving
stage_binding: 0 design
lane_fit: skill
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- algorithm_design
- worst_case
- guarantees
- robustness
- adversarial_input
cross_links:
- rel: related_to
  target_object_id: PAT_estimate_the_order_before_you_run_it
- rel: related_to
  target_object_id: PAT_state_the_approximation_guarantee_you_actually_have
- rel: related_to
  target_object_id: PAT_make_every_fast_path_redundant_with_the_general_one
- rel: related_to
  target_object_id: PAT_time_box_the_guess_and_name_the_fallback
reference:
  source_title: Algorithms in a Nutshell
  author: George T. Heineman, Gary Pollice, Stanley Selkow
confidence: high
references: []
variants: []
---

# Detect a Degrading Run and Switch to a Bounded Method

## Pattern Rule
**IF** you are relying on a method whose good behaviour is average-case only, and whose bad case is reachable by input you do not control
**THEN** find a quantity the run itself exposes that rises when the bad case is occurring, watch it as the work proceeds, and hand over to a method with a guaranteed bound when it crosses a threshold
**ELSE** where the bad case is merely unlikely rather than unreachable, say which of the two you have established, because an input nobody has sent yet is not an input nobody can send.

## Do
- Establish that the bad case is reachable rather than theoretical before building anything. The distinction is whether an input that triggers it can be constructed: for a partitioning sort choosing its pivot from three samples, an ordering exists that forces the quadratic case deliberately, and the existence of that construction is what turns a rare event into an available one.
- Pick a signal the run produces anyway. Recursion depth, iteration count, chain length in a bucket, retries against a backend — the useful one is already computed or nearly free to count, so watching it costs nothing on the runs that are behaving.
- Set the threshold from the good case's own shape, not from a round number. A divide-and-conquer method that halves its input should reach a depth near the logarithm of the size; exceeding twice that is the run reporting that it is not halving anything, and the threshold derives from the guarantee you expected rather than from taste.
- Require the fallback to be bounded, not merely different. Handing off to another method with the same average-case-only character relocates the problem; the fallback earns its place by having a proved worst case, and it is allowed to be slower in the ordinary case because it runs only when the ordinary case has already failed.
- Keep the answer identical across the switch. This is a repair to the time bound and not to the result, so a handover that changes which valid answer comes back has introduced a second behaviour that surfaces only on the inputs nobody tests.
- Prefer this to chasing a better average. Improving how a pivot is chosen, or how a hash is mixed, moves the bad case around without removing it, and past the first cheap improvement the effort buys a smaller probability of an event you have still not bounded.

## Don't
- Don't reach for the method with the proved worst case as the default instead. The average case is where nearly every run lives, and paying its cost everywhere to protect against an input that arrives rarely is usually the worse trade — the watchdog exists precisely so you can keep the fast default and still have a bound.
- Don't confuse this with guarding a fast path by its inputs. A fast path is chosen up front from a condition on the arguments and must return the same answer; this is chosen partway through from the observed behaviour of the run, because the inputs that trigger the bad case cannot be recognised cheaply by inspection — if they could, you would test for them at the door.
- Don't leave the fallback unexercised. It runs only on inputs that are rare by construction, so nothing in ordinary testing reaches it, and the branch that exists to save you is the branch least likely to work when it is finally entered.
- Don't watch a signal that only rises after the damage is done. A counter that crosses its threshold once the run has already spent most of its time has reported history rather than raised an alarm.
- Don't treat a measured absence of the bad case as a bound. Timings gathered on random input say nothing about ordered, adversarial, or heavily duplicated input, and those are the shapes that real data arrives in.

## Checklist
- Is the bad case reachable by a constructible input, or only improbable?
- What quantity does the run already expose that rises when it occurs?
- Does the threshold come from the guarantee you expected, and what is it in terms of the input size?
- Does the fallback have a proved bound, and does it return the same answer?
- What test drives the run into the fallback, and does it exist?

## Notes
The shape is worth naming because the instinct on discovering a bad worst case is to attack the choice that causes it, and that instinct is weakly rewarded. Better pivot selection genuinely helps on average and genuinely fails to remove the quadratic case; a partition method with a proved linear bound exists and is slow enough in practice to be of theoretical interest only. What resolves it is neither improving the default nor replacing it, but adding an observer: keep the fast method, notice when it is going wrong, and leave by a door that has a bound on it. A widely shipped standard-library sort is built exactly this way, monitoring its own recursion depth and switching to a heap-based sort when the depth says the partitioning has stopped dividing.

The cost structure is what makes it a good trade and is worth stating separately. The watchdog runs on every call and costs a comparison against a counter; the fallback runs almost never and costs more than the default would have; and the bound applies to every input including the constructed ones. Compare that with the alternative of defaulting to the bounded method, which pays its higher constant on every ordinary run to buy the same guarantee.

There is a second family this reaches, where the degradation comes from a distributional assumption rather than from an adversary. A method that partitions its input into buckets on the assumption that the keys spread evenly is linear when they do and quadratic when they crowd into a few buckets, and the parameter governing it — how many buckets — turns the same code from faster than a general sort into far slower. The signal there is the occupancy of the fullest bucket, and it is available for the same near-zero cost as recursion depth.
