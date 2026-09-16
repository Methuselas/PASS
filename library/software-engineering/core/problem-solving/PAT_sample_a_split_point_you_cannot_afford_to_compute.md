---
object_id: PAT_sample_a_split_point_you_cannot_afford_to_compute
object_type: pattern
name: Sample a Split Point You Cannot Afford to Compute
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
- randomization
- expected_cost
- recursion
cross_links:
- rel: related_to
  target_object_id: PAT_detect_a_degrading_run_and_switch_to_a_bounded_method
- rel: related_to
  target_object_id: PAT_decide_whether_the_split_or_the_combine_does_the_work
- rel: related_to
  target_object_id: PAT_estimate_the_order_before_you_run_it
reference:
  source_title: Algorithms
  author: Sanjoy Dasgupta, Christos Papadimitriou, Umesh Vazirani
confidence: high
references: []
variants: []
---

# Sample a Split Point You Cannot Afford to Compute

## Pattern Rule
**IF** the parameter that would make your algorithm efficient is as expensive to compute as the answer you are trying to produce
**THEN** choose it at random and bound the expected cost by how common acceptable choices are, instead of paying to find the best one or settling for a fixed choice that an adversarial input defeats.

## Do
- Notice the circularity before trying to break it by cleverness. Partitioning a list at its middle value would shrink the work by half each time, but finding that value is the very problem being solved, so any scheme that insists on it has to solve the problem to solve the problem.
- Define what counts as acceptable rather than ideal, and make it a range. A boundary anywhere in the middle half of the values shrinks the remaining work to three quarters, which is a worse ratio than a half and still leaves the total cost linear.
- Count how abundant the acceptable choices are, because that ratio is the whole argument. Half of any list lies within its middle half, so a value picked blindly is acceptable half the time, and on average two picks are needed before one lands — a constant, and constants do not change the growth rate.
- Say which distribution you are averaging over. The guarantee here is over the algorithm's own coin flips and holds for every input, which is what distinguishes it from an average taken over inputs you happen to expect and which a hostile caller can simply avoid supplying.
- Reach for the same move when there is no expensive parameter at all, only an input whose order you were about to assume was benign. Shuffling the input before processing it buys the identical guarantee by the identical argument: the cost now depends on your own draw rather than on the arrangement you were handed, so no particular input triggers the bad case and no hostile caller can construct one. The change is often a single line, and what it replaces is not code but an assumption nobody wrote down.
- Keep the worst case in view where it matters. Randomising makes the bad case improbable rather than impossible, so a system with a hard deadline needs either a fallback that caps the damage or a different algorithm.

## Don't
- Don't substitute a fixed rule for the random choice and assume you have the same guarantee. Always taking the first element is fast to compute and turns already-sorted input into the worst case, which is exactly the input most likely to arrive.
- Don't count on the draw to rescue heavily repeated values. When the candidates are all equal, every choice splits the work into everything but one element and nothing, however it is drawn: a randomly pivoted partition into smaller-or-equal and larger made exactly n(n−1)/2 comparisons on n equal values — 499,500 for a thousand, 7,998,000 for four thousand. The repair is in the partition rather than the draw: set the values equal to the chosen one aside in the same pass so they leave the recursion, and the same input took one comparison per element.
- Don't assume the caller cannot see the coins. The guarantee holds against an input fixed before the draws are made. Code the caller supplies that runs inside the algorithm — a comparison routine is the usual case — can decide how the values compare only as it is asked, choosing each answer to make the chosen split a bad one, and so drive a randomized sort to its worst case; so can a caller able to predict the generator. Where either is possible, the random choice needs a watchdog that bounds the run.
- Don't confuse an expected bound with an average over typical data. One is a property of the algorithm and survives any input; the other is a claim about the world that stops holding when the world changes.
- Don't assume a shuffle you wrote yourself is uniform. The obvious in-place version — walk the array and swap each element with one drawn from anywhere in the array — is biased, and the correct version differs only in drawing from the positions at or after the current one. Both produce output that looks thoroughly shuffled and passes every casual inspection, and only the second makes every arrangement equally likely. A guarantee resting on randomness is only as good as the randomness, so the shuffle is part of what has to be correct rather than a detail beneath it.
- Don't spend real effort improving the choice before checking whether it changes the growth rate. Sampling a few candidates and taking their middle value tightens the constant, and the constant was not what made the naive version slow.

## Checklist
- Does computing the ideal parameter require the answer you are computing?
- What range of choices is good enough, and what fraction of all choices falls in it?
- How many draws are expected before an acceptable one appears?
- Is your bound over the algorithm's own randomness, or over inputs you are assuming?
- What happens on the improbable bad run, and can the system tolerate it?
- Can the input be dominated by repeated values, and does the partition set equal values aside?

## Notes
The argument has three moves and all three are needed. First, relax the target from the best boundary to a band of good-enough ones. Second, show the band is a constant fraction of all possibilities, so a blind draw hits it with constant probability. Third, observe that a constant number of expected attempts multiplies the cost by a constant and therefore leaves the growth rate alone. Any of the three missing and the argument does not close; together they convert a circular requirement into a linear expected cost.

The distinction between randomness in the algorithm and assumptions about the input is the part that is easy to state and easy to forget under pressure. Deriving a bound from the algorithm's own coin flips means no caller can construct a bad case on purpose, because the caller does not control the coins — provided the caller cannot watch them being tossed. Deriving it from expected inputs means the bound holds until someone supplies unexpected ones, and the inputs most likely to be supplied — already ordered, reversed — are the ones the naive fixed choice handles worst, and heavily repeated values defeat every choice of a two-way split, random or not.
