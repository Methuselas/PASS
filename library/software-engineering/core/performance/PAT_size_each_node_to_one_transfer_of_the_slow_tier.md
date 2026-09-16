---
object_id: PAT_size_each_node_to_one_transfer_of_the_slow_tier
object_type: pattern
name: Size Each Node to One Transfer of the Slow Tier
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
- secondary_storage
- data_structures
- cost_model
cross_links:
- rel: related_to
  target_object_id: PAT_locate_the_working_set_on_the_memory_hierarchy
- rel: related_to
  target_object_id: PAT_repair_on_the_way_down_so_one_pass_never_backs_up
reference:
  source_title: Introduction to Algorithms
  author: Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, Clifford Stein
confidence: high
references: []
variants: []
---

# Size Each Node to One Transfer of the Slow Tier

## Pattern Rule
**IF** a linked structure is too large for fast memory, so that reaching a node means a transfer from a slower tier that moves data in fixed-size units
**THEN** count transfers as the cost, make each node exactly one transfer unit, and fill that unit with as many keys and child references as it holds, because the branching factor sets the height and the height sets how many transfers every lookup pays
**ELSE** where the whole structure stays in fast memory, the transfer count is not the cost, and node size should be chosen from what the processor's own memory levels reward.

## Do
- Keep two costs apart: the number of units read or written, and the processor time spent inside them. Positioning and fetching a unit from a mechanical disk takes milliseconds while scanning the unit's contents takes microseconds, so the transfer count dominates and is the number to design against.
- Make a node the size of one transfer unit and let that decide the branching factor. With keys small relative to the unit, a node can hold hundreds or thousands of children, and height falls with the logarithm taken in that base: a structure with a thousand keys and a thousand and one children per node reaches over a billion keys at height two.
- Keep the root in fast memory. A lookup then pays one transfer per level below it, so a height-two structure over a billion keys answers any lookup in at most two reads.
- Push bulky payload out of the interior nodes. Keeping only keys and child references in interior nodes and the associated data in the leaves, or behind a reference to its own unit, raises the interior branching factor and so lowers the height for the same unit size.
- Expect the search inside a node to move only the smaller cost. Once a unit is in fast memory, finding the right child is processor time; a binary search in place of a linear scan saves comparisons and leaves the number of transfers exactly where it was.

## Don't
- Don't reason about such a structure with the height of a binary tree. A binary tree over the same billion keys is around thirty levels deep, and every level is a transfer; the asymptotic class is the same and the cost is fifteen times worse.
- Don't let the node outgrow the unit. A node that spills into a second unit pays two transfers where the design assumed one, on every visit.
- Don't size by the key alone when payload travels with it. The branching factor is the unit size divided by the size of what the interior node actually stores, and satellite data stored beside each key divides it again.

## Checklist
- What is the transfer unit of the slow tier, and does one node fit exactly one?
- How many children does a node hold at that size, and what height does that give at the expected number of keys?
- Is the root held in fast memory?
- Do interior nodes carry payload that could live in the leaves or behind a reference?
- Is the design judged by transfers per operation, with processor time as the secondary measure?

## Notes
The move follows from a cost model in which one term is several orders of magnitude larger than the other. When reaching a node costs a mechanical wait of milliseconds and examining it costs microseconds, everything that reduces the number of nodes reached is worth more than anything that speeds up the examination, and the structure's shape should be chosen to minimise transfers even at the price of more work inside each node.

Branching factor is the lever because height is logarithmic in its base. Doubling the fan-out does not halve the number of levels, but moving from two to a thousand reduces a thirty-level path to three, and on a slow tier that is the difference between thirty waits and three. The same reasoning scales down the hierarchy wherever one level's transfer dominates the next level's work; the specific numbers change and the counting does not.
