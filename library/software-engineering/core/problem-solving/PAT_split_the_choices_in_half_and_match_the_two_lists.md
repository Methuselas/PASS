---
object_id: PAT_split_the_choices_in_half_and_match_the_two_lists
object_type: pattern
name: Split the Choices in Half and Match the Two Lists
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
- exhaustive_search
- meet_in_the_middle
- time_space_tradeoff
cross_links:
- rel: related_to
  target_object_id: AP_get_a_usable_answer_to_an_intractable_problem
- rel: related_to
  target_object_id: PAT_prune_a_partial_candidate_before_you_finish_building_it
- rel: related_to
  target_object_id: PAT_sweep_sorted_events_and_compare_only_neighbors
reference:
  source_title: Exact Exponential Algorithms
  author: Fedor V. Fomin, Dieter Kratsch
confidence: high
references: []
variants: []
---

# Split the Choices in Half and Match the Two Lists

## Pattern Rule
**IF** an exact answer needs a search over every subset or assignment of n independent items, and a candidate is judged by adding a quantity from one part of the items to a quantity from the other against a target or a limit that can be ordered — a sum that must equal a value, a total that must stay within a capacity
**THEN** split the items into two halves, list every choice within each half together with its quantity, order the lists, and find the matching pairs with one sorted scan, so the work grows with the square root of the number of subsets instead of with the number itself
**ELSE** where the condition cannot be ordered — every clause satisfied, every element covered — a good pair cannot be found by scanning, the two lists must be compared entry against entry, and the split saves nothing.

## Do
- Recognize the shape by its combination step. The quantity of a whole choice has to be computable from the two halves' quantities alone, and a fixed target or limit has to make "too small" and "too large" meaningful. Then a left entry that falls short rules out every smaller right entry, and one that overshoots rules out every larger one, which is what lets one pass over both sorted lists replace comparing every pair.
- Scan the two ordered lists from opposite ends. Start at the smallest left entry and the largest right entry; if the pair falls short, advance on the left, and if it overshoots, step back on the right. Each step discards an entry for good, so matching costs one pass over the lists on top of building them.
- Build each half's list already in order. Adding one item doubles the list, and merging the old list with its copy shifted by that item's quantity keeps it sorted, so no separate sort is needed. On subsets of random 40-bit numbers with an unreachable target, so that nothing stopped early, the split search took 1.9 ms at 32 items and 24 ms at 40, while trying every subset took 2,861 ms at 32. Brute force grew about sixteenfold with each four items added and the split search fourfold, and at 40 items it found all 20 reachable targets in 24 ms on average.
- Drop dominated entries before matching when the goal is the best total under a limit. An entry is dominated when another from the same half weighs no more and is worth at least as much. Once those are gone, a list sorted by weight is also sorted by value, so the best partner for a left entry is simply the heaviest right entry that still fits. On 0/1 knapsack with random 20-bit values and weights, the right list at 40 items shrank from 1,048,576 entries to 87, and the search took 103 ms. At 24 items it took 0.3 ms against 592 ms for trying every subset, with the same answer.

## Don't
- Don't use it where memory is the limit. Each list holds one entry per subset of its half, so the space grows as fast as the time. At 40 items the two lists held about a million 64-bit sums each, 16 MB in all; at 48 items, 256 MB. Splitting into more than two parts can bring the memory down, but it does not make matching faster.
- Don't split a condition that asks for coverage rather than a total. Requiring every clause of a formula to be satisfied by one half's assignment or the other's gives each half a vector that must reach at least one in every position. Such vectors have no order in which a shortfall rules out a whole run of partners, so every pair must still be checked.

## Checklist
- Is the quantity of a whole choice the sum of the two halves' quantities?
- Is the condition an equality or a limit, so that sorted order lets a scan discard partners?
- Are both halves' lists built in order, and matched in one pass from opposite ends?
- For a best total under a limit, have dominated entries been removed first?
- Will two lists of 2^(n/2) entries fit in the memory you have?

## Notes
The trade is the square root, and it comes from where the independence lies. Trying every subset of n items costs 2^n because each choice is paired with every choice for the remaining items. Once the items are split, each half has only 2^(n/2) choices, and a condition that orders the pairs lets you reject a run of partners at once. The combination step then becomes a sorted merge instead of a product, so 2^n turns into roughly 2^(n/2) with a logarithmic factor.

That is also why the method is fragile in exactly one place. Everything rests on the scan being allowed to discard a run of partners, and only an equality or a one-sided limit on a sum permits it. A coverage condition, where each position must be met by one side or the other, has no such run, and the split gains nothing there.
