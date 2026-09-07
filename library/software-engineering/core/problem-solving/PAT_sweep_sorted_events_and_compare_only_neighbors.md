---
object_id: PAT_sweep_sorted_events_and_compare_only_neighbors
object_type: pattern
name: Sweep Sorted Events and Compare Only Neighbors
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
- search
- ordering
- performance
cross_links:
- rel: related_to
  target_object_id: PAT_decide_whether_the_split_or_the_combine_does_the_work
- rel: related_to
  target_object_id: PAT_choose_a_problem_representation_before_solving
reference:
  source_title: 'Algorithms in a Nutshell: A Practical Guide'
  author: George T. Heineman, Gary Pollice, Stanley Selkow
confidence: high
references: []
variants: []
---

# Sweep Sorted Events and Compare Only Neighbors

## Pattern Rule
**IF** a problem asks about interactions among a set of objects — crossings, overlaps, closest pairs — and the direct approach compares every pair, costing time proportional to the square of the count
**THEN** sort the objects' relevant events into one order, sweep through that order while maintaining a live structure of only the objects currently active, and check interactions solely between neighbors in that structure as it updates
**ELSE** where the interactions you need are not confined to neighbors in any obtainable order, no sweep captures them, and pairwise comparison — or a different structure entirely — is the honest answer.

## Do
- Choose the sweep direction from the input, not from habit: a coordinate axis for geometric objects, a start-and-end time for intervals, any dimension the events can be linearly ordered along.
- Keep two structures in sync — an event queue that determines what happens next, and a state reflecting what is currently "live" at the sweep position, ordered so that objects able to interact are guaranteed to sit adjacent within it.
- Generate new events during the sweep, not only at the start, including speculative ones predicted from the current state — a computed intersection that would occur below the sweep line, say. Be ready to invalidate a speculative event if an intervening event changes the state that produced it before the sweep reaches it; a scheduled event is a prediction, not a certainty, until it is actually processed.
- Restrict every interaction check to neighbors in the live structure. The entire saving comes from proving that two objects far apart in the ordering cannot interact without first becoming neighbors — a check that reaches past neighbors has quietly gone back to comparing every pair.

## Don't
- Don't reach for this when the expected number of interactions is itself close to the square of the count. The bookkeeping of maintaining the state and the event queue can outweigh brute force exactly when there is little pruning to be had.
- Don't assume the order used for the sweep also orders the interactions within the live state at every moment. The state's own internal order usually has to be maintained or reasoned about separately as the sweep advances, because two objects can swap relative position as the sweep passes them.
- Don't leave events that land at the same sweep position unresolved. A tie-breaking rule has to be stated up front, or the state's neighbor invariant silently breaks at exactly the inputs most likely to occur in real data — already-sorted or already-aligned input.
- Don't lose sight of the fact that the algorithm's stated running time is a claim about the event queue's and live state's *own* operations, not just about the sweep's high-level shape. Back them with structures that actually deliver the insert, delete, and neighbor-lookup cost the analysis assumes — a plain heap with no membership check, or a linked list with linear-time insertion, will make the whole technique degrade silently to the brute force it was meant to beat, while the code still looks like the efficient algorithm.

## Checklist
- Is there a single dimension every event can be linearly ordered along?
- Does the live state actually maintain the invariant that only adjacent objects can interact?
- Are new events, including speculative ones, generated during the sweep and re-validated when reached, rather than only seeded once at the start?
- Is every interaction check reaching only immediate neighbors in the state, never past them?
- Is there an explicit tie-breaking rule for events landing at the same sweep position?
- Do the event queue and live state actually support the insert/delete/neighbor-lookup cost the algorithm's complexity claim depends on?

## Notes
This is a distinct shape from decomposing a problem by splitting it, choosing the best local step, filling a table of subproblems, or converting it into an already-solved one. Its move is to turn an all-pairs question into an adjacent-pairs question by finding an order the interactions respect, then paying for a live structure that maintains that order incrementally instead of recomputing it from scratch at every step.

The technique generalizes well past geometry. The same shape solves interval-overlap and meeting-scheduling problems — anywhere "consider only what's currently active" can replace "consider everything," the saving is the same, and the cost is the same: a state structure that has to stay correct as the sweep advances rather than being computed once.

The backing-structure warning is worth taking seriously rather than as a footnote: two independent implementations of this technique can differ by a full order-of-growth class purely because of which container holds the event queue or the live state, with nothing in the higher-level algorithm description revealing the difference. The complexity analysis is only as good as the data structures it silently assumes.
