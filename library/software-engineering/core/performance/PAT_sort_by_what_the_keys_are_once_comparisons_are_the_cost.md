---
object_id: PAT_sort_by_what_the_keys_are_once_comparisons_are_the_cost
object_type: pattern
name: Sort by What the Keys Are Once Comparisons Are the Cost
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
- lower_bound
- algorithm_choice
cross_links:
- rel: related_to
  target_object_id: PAT_ask_for_the_least_order_the_consumer_needs
- rel: related_to
  target_object_id: PAT_keep_the_order_of_equal_keys_when_it_carries_information
- rel: related_to
  target_object_id: PAT_detect_a_degrading_run_and_switch_to_a_bounded_method
- rel: related_to
  target_object_id: PAT_estimate_the_order_before_you_run_it
reference:
  source_title: Introduction to Algorithms
  author: Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, Clifford Stein
confidence: high
references: []
variants: []
---

# Sort by What the Keys Are Once Comparisons Are the Cost

## Pattern Rule
**IF** a full sort is measured as a real cost, a well-implemented comparison sort is already in use, and the keys are small integers, fixed-width values, or drawn from a distribution you know
**THEN** consider a sort that places elements by their key values rather than by comparing them, because no sort that learns order only through comparisons can use fewer comparisons than a multiple of n log n, and the only way past that bound is to use something about the keys
**ELSE** where order is defined only by a comparison routine, or the input is small, or memory is tight, keep the comparison sort — its remaining cost is constants, and the alternatives trade those constants for requirements the data may not meet.

## Do
- Recognise the ceiling before tuning further. A comparison sort that is already at n log n has nothing left to win but constant factors, so effort spent on it is bounded; effort spent on using the keys is not bounded by the same argument.
- Count into place when the keys lie in a small range. Tally how many keys take each value, turn the tallies into starting positions, and place each element directly; the cost is linear in the number of elements plus the size of the range, and placing from the end keeps equal keys in their original order. Measured on ten million keyed records in the range zero to a thousand, placing them this way took about 30 milliseconds against about 276 for a comparison sort, and every run of equal keys came out in its input order.
- Split wide fixed-width keys into digits when the range is too large to count directly. Sort once per digit, least significant digit first, with a pass that preserves the order of equal digits; choose digits of roughly log n bits so each pass counts over a range comparable to n. Measured on ten million 32-bit keys in four 8-bit passes, the digit sort took about 62 milliseconds against 634 for the comparison sort; 64-bit keys needed eight passes and took about 179 against 641.
- Distribute into buckets when the keys follow a distribution you can map to equal-probability intervals. Each bucket then holds few elements and sorts cheaply, and the total stays linear as long as the sum of the squared bucket sizes does — which is a claim about the input, so watch the fullest bucket.
- Measure against the comparison sort on the target machine and at the real sizes. The linear bound hides a constant per pass and a second buffer; which wins depends on the implementation, the machine's caches, and the data.

## Don't
- Don't count over a range much larger than the input. The range term then dominates: ten million keys spread over a billion values needed an eight-gigabyte tally array and took about 2.4 seconds, four times slower than simply comparing them. That is the case for digits, not for counting.
- Don't expect the linear sort to win on small inputs. On a thousand 64-bit keys the eight-pass digit sort took about 9 microseconds against about 6.5 for the comparison sort; the passes are a fixed cost the n log n term has not yet outgrown.
- Don't use a digit pass that disturbs equal digits. Each pass relies on the previous passes' order surviving among elements whose current digit is equal; an unstable pass silently destroys the lower digits' work and still produces output that looks mostly sorted.
- Don't choose this where memory is the constraint. The counting-based passes write into a second buffer the size of the input plus the tallies, where many comparison sorts work in place.
- Don't try to distribute an order that exists only as a comparison routine. A collation, a user-supplied comparator, or a multi-field rule with custom tie-breaking cannot be placed by value until it has been turned into keys whose digit order agrees with the routine exactly.

## Checklist
- Is the sort measured as a cost, and is the comparison sort already a good one?
- Are the keys integers in a small range, fixed-width values, or from a known distribution?
- For counting: is the range comparable to the number of elements?
- For digits: is each pass stable, and is the digit width near log n bits?
- Is there memory for a second buffer the size of the input?
- Does the measured result beat the comparison sort at the sizes that actually occur?

## Notes
The bound that makes this a decision rather than a trick comes from what a comparison can tell you. Each comparison answers one yes-or-no question, a correct sort must be able to end in any of the n! orderings of its input, and distinguishing n! outcomes needs at least log(n!) answers in the worst case, which is proportional to n log n. Merge sort and heapsort already meet it, so within the comparison model there is nothing asymptotic left to find. The sorts here are not faster comparison sorts; they ask a different kind of question — which value is this — and the bound says nothing about those.

The trade is always paid somewhere. Counting pays in a range-sized array, digit sorting pays in passes and a second buffer, and bucketing pays in an assumption about the distribution that the input may not honour. The measurements above favour the digit sort heavily at large sizes on one machine, but a comparison sort can use caches better and each digit pass does more work per element than a comparison pass, so the balance moves with the implementation and the machine — which is why the last Do is to measure rather than to trust either the bound or these figures.
