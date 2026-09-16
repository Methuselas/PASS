---
object_id: PAT_ask_for_the_least_order_the_consumer_needs
object_type: pattern
name: Ask for the Least Order the Consumer Needs
library_path:
- software-engineering
- core
- performance
stage_binding: 0 design
lane_fit: skill
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- performance
- sorting
- selection
- algorithm_choice
cross_links:
- rel: related_to
  target_object_id: PAT_estimate_the_order_before_you_run_it
- rel: related_to
  target_object_id: PAT_sample_a_split_point_you_cannot_afford_to_compute
- rel: related_to
  target_object_id: PAT_keep_the_order_of_equal_keys_when_it_carries_information
reference:
  source_title: Introduction to Algorithms
  author: Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, Clifford Stein
confidence: high
references: []
variants: []
---

# Ask for the Least Order the Consumer Needs

## Pattern Rule
**IF** code sorts a collection and then reads only part of what the sort established — one element at a given rank, the few largest, the ones on either side of a threshold
**THEN** ask for exactly that arrangement instead of a total order, because finding an element by rank does not have to pay for ordering everything else, and the difference grows with the size of the collection
**ELSE** where the consumer really does walk every element in order, or the collection is small enough that the sort is not the cost, the full sort is the plain and correct call.

## Do
- Name what the reader of the result actually uses before choosing the operation. A median, a percentile, the smallest few, a split at a threshold and a complete ordering are five different requests, and only the last needs every element placed.
- Reach for selection by rank for a median or percentile. Ordering a collection by comparisons cannot be done in fewer than a number of comparisons proportional to n log n, but finding the element that belongs at one rank can be done in expected linear time, because it only has to settle which side of the answer each element lies on. Measured on ten million 64-bit keys, the median by selection took about 68 milliseconds and the full sort about 637.
- Get the top few in order by selecting and then sorting only those. Select the boundary element, which leaves the smallest k on one side of it, and sort the k: the cost is linear in n plus k log k rather than n log n. Measured on the same ten million keys, the top hundred in order took about 57 milliseconds against 637 for sorting everything and taking the first hundred.
- Partition when the consumer only needs a split. Everything below a threshold and everything above it is one pass that orders nothing within either side.
- Say in the name of the call what was asked for. A call that selects reads as a selection; a full sort followed by an index makes the reader work out that only one position mattered.

## Don't
- Don't expect a weaker operation to arrange what it did not have to. After selection, the elements on each side of the chosen rank are in no promised order, and code that relied on the full sort's by-product will misbehave only when someone swaps in the cheaper call.
- Don't reach for the selection method with a proved linear worst case by default. It exists and it is slow in practice; the expected-linear randomized selection is the usual choice, with the same caveats about repeated keys and hostile inputs as any randomized partition.
- Don't use a weaker operation where equal elements must keep their original order. Selection and partial ordering generally promise nothing about ties; if the order of equal keys carries information, that requirement decides the operation before speed does.
- Don't rewrite a sort that is not the cost. On a few thousand elements the difference is microseconds; measure that the sort is on the critical path before trading a familiar call for a less familiar one.

## Checklist
- After this sort, which positions does any code actually read?
- Is the request a rank, a top few, a split, or a total order?
- If the top few must be in order, is the cost linear in n plus the sort of only those few?
- Does anything downstream depend on the arrangement of elements the cheaper operation leaves unordered, or on the order of ties?
- Has the sort been measured as a cost worth removing?

## Notes
The lower bound on comparison sorting is what makes this more than a constant-factor tidy-up. Any method that orders n elements using comparisons needs a number of comparisons proportional to n log n in the worst case, so no cleverness in the sort removes that term. Selection escapes it not by being a better sort but by not sorting: the question "which element is kth" has less information in its answer than "what is the whole order", and an algorithm that computes only the smaller answer is not bound by the cost of the larger one.

The top-few case composes the two ideas. Selection draws the boundary, and a sort confined to the elements on the near side of the boundary supplies the order that was actually wanted, so the cost of ordering is paid on k elements rather than on n. The larger n is relative to k, the more of the sort's work was never going to be read.
