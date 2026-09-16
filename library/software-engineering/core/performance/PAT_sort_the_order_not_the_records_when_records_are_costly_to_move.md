---
object_id: PAT_sort_the_order_not_the_records_when_records_are_costly_to_move
object_type: pattern
name: Sort the Order, Not the Records, When Records Are Costly to Move
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
- sorting
- data_movement
- permutation
- memory_access
cross_links:
- rel: related_to
  target_object_id: PAT_sort_by_what_the_keys_are_once_comparisons_are_the_cost
- rel: related_to
  target_object_id: PAT_ask_for_the_least_order_the_consumer_needs
- rel: related_to
  target_object_id: PAT_spend_computation_to_buy_sequential_access
- rel: related_to
  target_object_id: PAT_predict_cost_from_counted_operations_and_measured_unit_costs
reference:
  source_title: An Introduction to the Analysis of Algorithms
  author: Robert Sedgewick, Philippe Flajolet
confidence: high
references: []
variants: []
---

# Sort the Order, Not the Records, When Records Are Costly to Move

## Pattern Rule
**IF** the records to be sorted are much larger than their keys, so that moving a record costs far more than comparing two keys
**THEN** sort a compact array of key-and-position pairs instead, and then either read the records through the order that results or apply that order once, in place, by following its cycles, which moves each record at most once
**ELSE** where a record is not much larger than a key and a position, sort the records directly — the extra array and the extra pass cost more than the moves they save.

## Do
- Count moves as well as comparisons. A general sort moves each record many times on its way to its final place: a library comparison sort over a million 64-byte records copied records 30.9 times per record, while applying the finished order by cycles copied them 1.0 times per record.
- Carry the key into the array you sort. Pairs of key and position sit in one contiguous array and compare without touching the records; comparing positions by looking up each record's key fetches two scattered records per comparison. On two million 256-byte records, sorting the pairs and applying the order took 272 ms, sorting positions through a lookup 438 ms, and sorting the records directly 401 ms.
- Find the crossover by record size on the target machine. On two million records, the direct sort took 122, 151, 199 and 401 ms at 16, 64, 128 and 256 bytes, against 202, 209, 240 and 272 ms for pairs; at 1 KB, on half a million records, it was 368 against 106. The crossover fell between 128 and 256 bytes, and was the same at a hundred thousand records.
- Apply the order by cycles. The sorted pairs say that the record now at position order[i] belongs at i. For each position not yet in place, save its record; then repeatedly move in the record that belongs there, mark that position finished by setting order[j] = j, and step to the position it came from, until the cycle returns to the start, where the saved record goes. Every record out of place moves once, plus one save per cycle.
- Leave the records where they are if the consumer only walks them in order a few times. Reading all two million 256-byte records through the order took 27 ms against 8 ms once the order was applied, and applying it cost about 120 ms, so applying paid for itself only after about six full ordered passes; at 1 KB, about twenty.

## Don't
- Don't use the indirection for small records. At 16 bytes the pairs took 202 ms where sorting the records directly took 122; the saved moves were cheaper than the second array and the extra pass.
- Don't apply the wrong permutation. What the sort produces is where each place's record currently is; the rank of each record in its current place is the inverse of that, and applying one where the other is meant scrambles the data.
- Don't expect the order array to survive being applied. The in-place pass marks each finished position by overwriting its entry, so copy the order first if anything needs it afterwards.

## Checklist
- How large is a record compared with a key and a position, and where does the measured crossover fall?
- Does the sorted array carry the keys, so comparisons never touch the records?
- Does the consumer need the records moved, or only read in order, and how many times?
- Is the order being applied the one that says where each place's record is now?
- Is a copy of the order kept if it is needed after the in-place pass?

## Notes
Sorting has two costs that grow differently: comparisons scale with the keys and moves scale with the records. A direct sort ties them together, paying the record's full size every time it shuffles an element on the way to its place. Sorting the order separates them. The comparisons run over small, adjacent pairs, and the large records move once each at the end, or never if they only need to be read in order.

In-place application stays cheap because a random order has few cycles, about the natural logarithm of the number of records. The one save and restore per cycle is therefore negligible beside the one move per record. Most records sit on a few long cycles, the longest averaging about three fifths of all records, so the pass itself visits positions in a scattered order, and it pays that once.
