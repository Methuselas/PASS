---
object_id: PAT_parallelize_the_combine_step_or_it_becomes_the_bottleneck
object_type: pattern
name: Parallelize the Combine Step or It Becomes the Bottleneck
library_path:
- software-engineering
- core
- concurrency
stage_binding: 0 design
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- concurrency
- design
- divide_and_conquer
- scalability
cross_links:
- rel: related_to
  target_object_id: PAT_derive_the_parallelism_from_work_and_span
- rel: related_to
  target_object_id: PAT_decide_whether_the_split_or_the_combine_does_the_work
reference:
  source_title: 'Introduction to Algorithms, 3rd Edition'
  author: Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, Clifford Stein
confidence: high
references: []
variants: []
---

# Parallelize the Combine Step or It Becomes the Bottleneck

## Pattern Rule
**IF** a divide-and-conquer algorithm's recursive calls run in parallel but its combine step is left serial, and the combine step does linear work at every level
**THEN** look for a way to make the combine step itself recursively divisible — typically by finding, through a search, a consistent split point across every input being combined so the combine reduces to two independent sub-combines of comparable size — rather than accepting the serial combine as fixed
**ELSE** where the combine step is already constant or logarithmic time, parallelizing the recursion alone is enough and there is nothing further to buy here.

## Do
- Compute the parallelism the naive parallel-recursion version actually achieves — work divided by span — before assuming the split was the whole job. A recursive split with a linear serial combine at every level gives a span that is itself linear, and dividing a log-linear amount of work by a linear span leaves only logarithmic parallelism: real, but nowhere near enough to use more than a handful of processors regardless of how large the problem grows.
- Look inside the combine step for the same shape the outer algorithm already has. A merge of two sorted sequences looks inherently sequential — each output position seems to depend on having placed the one before it — but it is not: locating where the median of one sequence falls in the other (a search, not a scan) splits the merge into two independent halves that can themselves be merged in parallel, recursively.
- Recompute the span of the combine step once it is parallelized, and propagate that number back into the whole algorithm's span. A logarithmic-work search performed at every level of a logarithmic-depth recursion yields a span of about the square of a logarithm — small enough that the total parallelism becomes close to the total work, which is the actual goal.
- Expect the fix to look more complex than the step it replaces. A binary search that locates matching split points across two inputs is more code than the three-line loop it replaces, and that extra complexity is the price of turning a linear serial step into a logarithmic parallel one.

## Don't
- Don't declare an algorithm "not parallelizable enough" from a design that parallelized only the split and left the combine untouched. The combine step is exactly where to look next, not a fixed cost to accept.
- Don't parallelize the combine step by simply splitting its input in half without checking that both halves stay correctly related to the corresponding halves of the other input. A combine step usually has a correctness invariant — every element before the split point in one input must line up with every element before the corresponding point in the other — and an arbitrary split breaks that invariant even though it superficially "divides the work."
- Don't stop at getting the combine step to run in parallel at all. A combine step parallelized into two pieces that are wildly uneven in size reproduces the same bottleneck one level down; the split point has to divide the work close to evenly to be worth the added complexity.

## Checklist
- Does the combine step do more than constant or logarithmic work at each level of the recursion?
- Has the combine step's own span been computed, not just assumed to be small because it "runs alongside" the parallel recursive calls?
- Is there a search, rather than a scan, that can locate a consistent split point across every input the combine step touches?
- Once the combine step is parallelized, does the recomputed overall span actually change the algorithm's parallelism, or does something else now bind?
- Are the two halves the parallelized combine step produces close to balanced in size?

## Notes
This is the concrete fix for the case `PAT_derive_the_parallelism_from_work_and_span` predicts but does not itself resolve: when the longest dependency chain is what binds, that card says restructuring is the only remedy and to recompute the chain afterward — this card is what that restructuring usually looks like in a divide-and-conquer algorithm specifically, because the combine step is where such algorithms hide their serial cost by convention rather than by necessity.

The habit worth keeping is treating "this step looks sequential" as a hypothesis rather than a fact, the same way a search replaces a scan elsewhere in algorithm design. A step's serial appearance in the pseudocode is a property of how it was written, not a property of the problem it solves — the merge step looked sequential for the same reason any accumulation loop looks sequential, and it stopped looking that way the moment the question became "where would this element go" instead of "what is the next element."
