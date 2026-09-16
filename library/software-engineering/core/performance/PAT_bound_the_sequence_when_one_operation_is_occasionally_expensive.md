---
object_id: PAT_bound_the_sequence_when_one_operation_is_occasionally_expensive
object_type: pattern
name: Bound the Sequence When One Operation Is Occasionally Expensive
library_path:
- software-engineering
- core
- performance
stage_binding: 0 design
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- performance
- amortized_analysis
- cost_model
- data_structures
- latency
cross_links:
- rel: related_to
  target_object_id: PAT_estimate_the_order_before_you_run_it
- rel: related_to
  target_object_id: PAT_keep_a_spare_before_releasing_capacity
- rel: related_to
  target_object_id: PAT_report_the_spread_not_just_the_number
reference:
  source_title: Introduction to Algorithms
  author: Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, Clifford Stein
confidence: high
references: []
variants: []
---

# Bound the Sequence When One Operation Is Occasionally Expensive

## Pattern Rule
**IF** an operation is cheap nearly always and occasionally expensive — a container that reallocates, a counter that carries, a buffer that flushes, a structure that rebalances — and you need to say what it costs
**THEN** bound the total cost of a sequence of operations and divide by their number, rather than quoting the worst single operation, and label the result an amortized bound
**ELSE** where the expensive case can occur on every operation with no cheap ones in between, there is nothing to spread the cost over and the per-operation worst case is the honest number.

## Do
- Choose whichever accounting makes the argument shortest, because the three available are equivalent in what they prove. Bounding the whole sequence at once and dividing is the least machinery; charging each operation more than it costs and holding the surplus against the objects is easier when different operations deserve different charges; defining one quantity over the whole structure that rises during the cheap operations and falls to pay for the expensive one handles the hardest cases, including structures that both grow and shrink.
- Keep the charges out of the code. They exist to make the argument go through, and a field holding an object's accumulated credit is the analysis leaking into the implementation — storage occupied by a number that nothing ever reads.
- Say amortized only when you mean amortized. It is a worst-case claim about every possible sequence, with no probability in it. Average-case is a claim about a distribution of inputs, and it fails when the inputs are not drawn from that distribution. The two sound interchangeable and promise entirely different things to a caller.
- Verify the cheap operations genuinely arrive before the expensive one they pay for. The surplus has to be non-negative at every point in the sequence; a scheme that undercharges early and intends to recover later has not bounded anything, because the sequence can end at the moment it is furthest behind.
- Let the analysis correct the design rather than merely describe it. Doubling a table when it fills and halving it when it falls half empty reads as pleasingly symmetric and is the defect: a workload alternating one insertion and two deletions at the boundary pays a full copy on nearly every operation. Halving only at a quarter full leaves enough slack after either resize that the next one must be earned.
- Keep in view that the expensive operation still happens. An amortized bound says the sequence is cheap; it says nothing about the individual call that reallocates, and that call takes its full time when it arrives.

## Don't
- Don't quote the per-operation worst case for a structure whose expensive step is rare. Saying an append to a growable array costs time proportional to its length is true, is what the worst case supports, and describes a cost that almost no append pays.
- Don't accept an amortized bound where a single slow operation is the actual problem. A frame deadline, a request timeout, or an interactive response is a constraint on the worst call, not on the average of many, and a structure with an excellent amortized bound can miss it every time it resizes. The remedy there is a scheme that spreads the work across operations rather than one that merely accounts for it afterwards.
- Don't let the running surplus go negative on any prefix of the sequence. The bound is a claim about every prefix, not only about the end.
- Don't assume the bound survives a new operation. Adding an operation that undoes the one the accounting was built around — a decrement beside an increment, a delete beside an insert — can restore the bad case that the original analysis ruled out, without changing any existing code.

## Checklist
- Is the expensive step rare because of something structural, or only because your workload has not triggered it yet?
- Does the surplus stay non-negative at every point in the sequence, not just at the end?
- Is the figure being reported an amortized bound or an average over assumed inputs, and does the wording say which?
- Does anything here constrain the slowest single call rather than the total?
- If an operation were added that reverses the one being amortized, would the argument still hold?

## Notes
The distinction that does the most work here is between amortized and average-case, because they are routinely conflated and only one of them is a guarantee. An amortized bound is derived without probability: it holds for every sequence of operations, including one constructed by somebody trying to break it. An average-case bound holds over a distribution and says nothing about a particular adversarial or merely unusual input. A structure described as "constant time on average" may have either property, and which one it has determines whether the description survives contact with hostile input.

The second point worth carrying is that the analysis is a design tool and not only a description. Working out what pays for a resize is what exposes the symmetric grow-and-shrink thresholds as a thrashing bug, and the fix — separating the two thresholds so neither resize leaves you adjacent to the other — is visible from the accounting rather than from the code. That is the general shape: the step where the argument refuses to close is usually the step where the design is wrong.

Where this reasoning does not reach is latency, and the gap matters more now than when the technique was developed. Spreading cost across a sequence is exactly the right model for total throughput and exactly the wrong one for a system with a deadline on each individual response. A structure that is constant time amortized and occasionally linear in the worst call will meet a throughput target and miss a tail-latency target, and no amount of refining the amortized figure will change that — the question being asked is a different one.
