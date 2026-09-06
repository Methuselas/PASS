---
object_id: PAT_decide_whether_the_split_or_the_combine_does_the_work
object_type: pattern
name: Decide Whether the Split or the Combine Does the Work
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
- recursion
- algorithm_design
- decomposition
- performance
cross_links:
- rel: related_to
  target_object_id: PAT_bound_recursion_before_you_reach_for_it
- rel: related_to
  target_object_id: PAT_estimate_the_order_before_you_run_it
reference:
  source_title: Algorithms
  author: Sanjoy Dasgupta, Christos Papadimitriou, Umesh Vazirani
confidence: high
references: []
variants: []
---

# Decide Whether the Split or the Combine Does the Work

## Pattern Rule
**IF** you are designing an algorithm that solves a problem by breaking it into smaller instances of the same problem
**THEN** decide deliberately which side of the recursion carries the effort — a cheap split paid for by a careful combine, or a careful split that leaves nothing to combine — rather than letting both sides accumulate work by default.

## Do
- Locate the effort in an algorithm you already know before designing a new one. Sorting by halving an array at its midpoint does nothing on the way down and all its work on the way back up, merging sorted runs. Finding the kth smallest element does the reverse: it partitions around a chosen value, and once the recursive call returns there is nothing left to do.
- Prefer the careful split when it lets you discard subproblems. Partitioning a list around a value tells you which part holds the answer, so only one part is searched and the others are dropped — the difference between solving every piece and solving one of them, and it changes the growth rate rather than a constant.
- Prefer the cheap split when every piece contributes to the answer. If the result needs all the subresults anyway, effort spent choosing the boundary buys nothing, and a boundary chosen without inspecting the data is free.
- Count the subproblems as a separate question from their size. Restructuring the arithmetic so that multiplying two numbers takes three half-sized products instead of four, or two matrices seven instead of eight, buys a saving at every level at the cost of extra additions — the same constant saved outside a recursion would not be worth the ingenuity.
- Stop descending at the size where a primitive already does the job. The recursion's mathematical base case is one element; its useful base case is whatever the machine or the standard library handles in one step, and below that the bookkeeping costs more than the work.

## Don't
- Don't pay on both sides without noticing. Work in the split and work in the combine are alternatives, and an algorithm that inspects the data carefully to divide it and then still has a substantial merge is usually solving the problem twice.
- Don't treat the number of subproblems as fixed by the problem. It is fixed by the decomposition you chose, and a decomposition that produces fewer of them is a different algorithm with a different growth rate.
- Don't design the recursion around the base case. The base case is where the recursion stops, not where the algorithm earns its speed, and reasoning that starts there tends to produce the naive decomposition.

## Checklist
- Which side of your recursion does the real work, and can you say so in one sentence?
- Does the split let you discard any subproblem, or must every piece be solved?
- How many subproblems does each level create, and would restructuring produce fewer?
- At what size do you hand off to a primitive instead of recursing further?

## Notes
The misconception this addresses is that the decomposition belongs to the problem. It does not. The same problem admits both arrangements, and which one you end up with is settled by a single earlier choice — whether you look at the data before dividing it — made so early and so quietly that it rarely registers as a decision at all. A designer who has met only one of the two arrangements will reproduce it everywhere, including where the other one would have discarded most of the work.

The count of subproblems deserves its own attention because it enters the cost differently from everything else. The size of each subproblem sets how deep the recursion goes; the count sets how wide it becomes, and width compounds. This is why an algebraic rearrangement that looks like a rounding error in isolation — three multiplications where four were expected — changes the exponent rather than the constant, and why the reverse mistake is expensive in the same proportion.
