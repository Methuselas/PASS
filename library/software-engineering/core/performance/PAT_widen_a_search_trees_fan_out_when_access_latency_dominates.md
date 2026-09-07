---
object_id: PAT_widen_a_search_trees_fan_out_when_access_latency_dominates
object_type: pattern
name: Widen a Search Tree's Fan-Out When Access Latency Dominates
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
- data_structures
- memory
- design
cross_links:
- rel: related_to
  target_object_id: PAT_locate_the_working_set_on_the_memory_hierarchy
- rel: related_to
  target_object_id: PAT_choose_the_data_structure_for_the_dominant_access_pattern
reference:
  source_title: 'Introduction to Algorithms, 3rd Edition'
  author: Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, Clifford Stein
confidence: high
references: []
variants: []
---

# Widen a Search Tree's Fan-Out When Access Latency Dominates

## Pattern Rule
**IF** a search structure's cost is dominated by a fixed latency per access to the next level — a disk seek, a network round trip, a cache-line fetch — rather than by how much work happens once that level is reached
**THEN** widen the structure's branching factor to whatever one access unit can carry, trading more comparisons per access for fewer accesses overall, because a search's height falls logarithmically with the branching factor while extra scanning inside an access already being paid for is comparatively free
**ELSE** where every access already costs about the same regardless of how much is fetched with it — an in-memory structure living at cache or register speed — a narrow branching factor with cheap per-node comparisons is the better trade, and widening the node only adds work with nothing to buy back.

## Do
- Identify the actual unit of access before sizing anything. A disk read moves a whole page regardless of how much of it is used; a network round trip pays its latency regardless of payload size; a cache-line fetch moves a fixed number of bytes whether one or all of them matter. The branching factor should match what one access unit can hold, not an arbitrary small constant.
- Compute the height that follows from the branching factor and compare it to what a narrow structure would need. A branching factor in the hundreds or thousands turns a search over a billion items into a handful of accesses instead of thirty; that reduction in accesses is the entire payoff, and it exists only because each access already had to happen at that latency regardless of size.
- Accept more comparisons per level in exchange for fewer levels. Once an access unit is in hand, scanning hundreds of entries within it costs nothing next to the latency already paid to fetch it — the two costs are not on the same scale, and treating them as comparable is the mistake this design corrects.
- Recompute the trade-off when the access unit changes. A structure sized for disk pages is oversized once its working set fits in memory, and a structure sized for memory is undersized the moment part of it has to live on slower storage; the right branching factor is a property of where the data lives, not of the structure's logic.

## Don't
- Don't apply this reasoning to a structure whose accesses are already uniformly cheap. Widening a node that lives entirely in cache adds comparison work without buying back any latency, since there was no per-access cost being amortized in the first place.
- Don't assume a wider node is free to search once fetched. The cost inside a fetched unit still has to be paid — for a moderate number of entries a scan within it is the honest choice, but past some size a small structure inside the node pays for itself, and that crossover is worth checking rather than assumed away.
- Don't confuse this with a general "bigger blocks are better" rule. The saving comes specifically from a fixed, large per-access cost; where that cost is small or absent, a wide fan-out only adds bookkeeping with nothing to amortize it against.

## Checklist
- Is there a real, fixed latency per access to the next level of this structure, distinct from the cost of using what gets fetched?
- Has the branching factor been sized to what one access unit can carry, rather than picked as an arbitrary small constant?
- Has the resulting height been compared against a narrower alternative, to confirm the accesses saved are worth the change?
- Would the right branching factor change if the data's location in the memory hierarchy changed?

## Notes
This generalizes past disks. The same reasoning justifies wide-fanout structures wherever a fixed round-trip cost dominates — a distributed lookup service, an in-memory index sized to cache lines rather than to individual keys — and it is the same shape as batching in general: pay the fixed cost once, carry as much useful work across it as the unit allows.

The insight is easy to state and easy to apply wrongly if the "why" is dropped: it is not that wide nodes are inherently better, it is that a specific, large, per-access cost changes what "more work per access" is being traded against. Remove that cost and the trade reverses — which is exactly why the same structure that is right for a database index on disk is wrong for the equivalent lookup held entirely in memory.
