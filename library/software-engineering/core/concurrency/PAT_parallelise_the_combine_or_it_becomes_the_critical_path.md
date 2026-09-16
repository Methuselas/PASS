---
object_id: PAT_parallelise_the_combine_or_it_becomes_the_critical_path
object_type: pattern
name: Parallelise the Combine, or It Becomes the Critical Path
library_path:
- software-engineering
- core
- concurrency
stage_binding: 0 design
lane_fit: skill
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- concurrency
- parallelism
- divide_and_conquer
- critical_path
- span
cross_links:
- rel: related_to
  target_object_id: PAT_derive_the_parallelism_from_work_and_span
- rel: related_to
  target_object_id: AP_design_a_parallel_decomposition
- rel: related_to
  target_object_id: PAT_decide_whether_the_split_or_the_combine_does_the_work
- rel: related_to
  target_object_id: PAT_decide_if_the_problem_is_worth_parallelizing
reference:
  source_title: Introduction to Algorithms
  author: Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, Clifford Stein
confidence: high
references: []
variants: []
---

# Parallelise the Combine, or It Becomes the Critical Path

## Pattern Rule
**IF** you have parallelised a recursive algorithm by letting its subproblems run concurrently, and the speedup falls far short of what the machine offers
**THEN** look at the step that combines the subresults, because a serial combine lies on every path through the computation and caps the available parallelism however well the division itself parallelises
**ELSE** where the combine is already a fixed-cost step — nothing to merge, subresults written into places that do not overlap — the division is the whole algorithm and the chain is already as short as it can be.

## Do
- Compute the ratio instead of trusting how parallel the code looks. Halving the input and running both halves at once reads as thoroughly parallel, and with a combine that costs time proportional to its input the longest dependent chain is proportional to the *whole* input — the topmost combine alone touches every element. The parallelism that survives is then merely logarithmic in the input size: enough to keep a handful of processors busy, and nowhere near enough for hundreds.
- Treat "inherently serial" as a claim to test rather than a property to accept. Merging two sorted sequences reads as a strictly sequential walk with a carry of state between steps, and it decomposes anyway: take the middle element of the larger sequence, locate by binary search where it belongs in the other, and the two resulting halves of the merge share nothing and can proceed independently.
- Expect the combine's own decomposition to be recursive, and to cost something. Splitting a merge this way turns a chain proportional to the input into one proportional to a small power of its logarithm, which is the entire gain; it also performs searches and copying that the serial version did not.
- Recheck the ratio after restructuring, because that number is the reason the change was made. The total work should stay within a constant factor of what it was, while the chain is what the restructuring exists to move — and a change that lengthens the work without shortening the chain has cost you twice.
- Coarsen the base case last, and knowingly. Below some size the bookkeeping outweighs the parallelism, and switching to an ordinary serial routine there trades a little of the available parallelism for a large constant-factor gain. Do it after the chain is short, not instead of shortening it.

## Don't
- Don't read a parallel-looking structure as evidence of parallelism. Two recursive calls running side by side is the part that is easy to see and easy to write, and it is not where the limit usually sits.
- Don't attack the division when the combine is what binds. Spawning more aggressively, splitting into more pieces, or tuning the scheduler all leave a serial combine exactly as long as it was, and the finish time does not move.
- Don't accept the first parallel version because it beats the serial one. Faster on four processors and no faster on four hundred is the exact signature of this problem, and testing on a small machine cannot distinguish it from a version that scales.
- Don't assume the parallel combine is free of new failure modes. It writes subresults into regions that must genuinely not overlap, and the argument that they do not is now part of the algorithm's correctness rather than an obvious property of a sequential walk.

## Checklist
- What is the longest dependent chain, and how much of it is the combine step?
- Is the combine's cost proportional to its input, and is it running serially?
- What is the parallelism figure, and how does it compare with the processor count you intend to use?
- Has the total work grown by more than a constant factor in exchange for the shorter chain?
- Does the parallel combine write into regions that provably do not overlap?
- Was this measured on a machine large enough to show the limit?

## Notes
The reason this is worth naming rather than leaving to a general instruction to shorten the critical path is that it says where to look. Knowing that the longest chain governs the achievable speedup does not, by itself, tell anybody which part of their algorithm is contributing it, and in a recursive decomposition the answer is systematically the same: the division is the part that obviously parallelises and the combination is the part that quietly does not. A rule of thumb that names the usual culprit is worth more here than a correct principle that leaves the search open.

The second half — that a combine which looks sequential often is not — is where the real work is, and it does not come for free. The parallel form needs a way to split the combining task into independent pieces, which typically means finding a point in one input and locating the corresponding point in the others, and that search is extra work the serial version never did. The trade is deliberate: a larger total work term bought in exchange for a dramatically shorter chain. It pays whenever the processor count is large enough that the chain, rather than the work, is what binds, and it is a poor trade on a small machine.

Worth keeping in view is that this reasoning lives entirely in the model that counts steps and dependencies, and that model ignores memory traffic, cache behaviour, and the cost of moving subresults between processors. A restructuring that improves the chain and multiplies the data movement can lose in practice while winning on paper, so the ratio establishes whether the algorithm permits the speedup, and only measurement establishes whether this machine delivers it.
