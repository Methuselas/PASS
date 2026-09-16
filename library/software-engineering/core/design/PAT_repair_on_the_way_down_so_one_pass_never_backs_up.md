---
object_id: PAT_repair_on_the_way_down_so_one_pass_never_backs_up
object_type: pattern
name: Repair on the Way Down So One Pass Never Backs Up
library_path:
- software-engineering
- core
- design
stage_binding: 0 design
lane_fit: skill
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- data_structures
- hierarchical_structures
- invariants
- secondary_storage
cross_links:
- rel: related_to
  target_object_id: PAT_keep_a_structural_invariant_loose_enough_to_repair_locally
- rel: related_to
  target_object_id: PAT_store_the_derived_value_whose_updates_stay_local
reference:
  source_title: Introduction to Algorithms
  author: Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, Clifford Stein
confidence: high
references: []
variants: []
---

# Repair on the Way Down So One Pass Never Backs Up

## Pattern Rule
**IF** you are changing a hierarchical structure from the top down, and the change at a lower level can overflow or underflow a node so that the repair must propagate back up toward the root
**THEN** fix the condition before you descend — split a node that is already full, top up a node that is already at its minimum — so the change can finish in one downward pass instead of propagating a repair back up the path
**ELSE** where revisiting ancestors is cheap and nothing is held per level — everything in fast memory, no concurrent readers — the repair-afterwards version does fewer structural changes and is simpler to prove.

## Do
- Strengthen the condition you guarantee on arrival at each node by exactly the margin the child operation can consume. Before descending to insert, make sure the child is not full, so a split there always has room for the key it pushes up; before descending to delete, make sure the child holds one more key than the minimum, so removing from it can never leave it too small.
- Repair at the parent, with both nodes in hand. Splitting a full child pushes its median into a parent you already know is not full; topping up a minimal child borrows through the parent from a sibling or merges the two around the separating key. The parent is the node you just came from, so no path back up has to be remembered.
- Handle the root first as its own case. A full root splits under a new root before descent begins, and that is the only way the structure grows in height; a root left with no keys by a merge is removed, and that is the only way it shrinks.
- Use it where each level visited costs something to hold. Descending in one pass means only a constant number of nodes need to be present at any moment — on secondary storage, a constant number of pages in memory regardless of the height — and no stack of ancestors has to be kept for a return trip.

## Don't
- Don't count the preemptive repairs as free. Splitting every full node met on the way down will sometimes split a node the insertion would never have overflowed, because the key lands elsewhere; the single pass is bought with occasional structural work that a repair-afterwards version would have skipped.
- Don't guarantee only the ordinary minimum on arrival. A child that arrives exactly at the minimum is still legal and still the one case the downward pass cannot handle, because removing from it forces a repair that has to reach back up.
- Don't claim the pass never returns when the item being removed sits in an interior node. It is replaced by its nearest neighbour in order, found and removed further down in the same pass, and the pass may have to come back to that one interior node to write the replacement — a single bounded return, not a walk back up the path, but a return all the same.

## Checklist
- Which operations can overflow or underflow a node, and by how much can one child operation change a node's count?
- Is the condition guaranteed on arrival strong enough to absorb exactly that change?
- Is the root handled before descent, as the only place height changes?
- How many nodes must be held at once, and is that constant in the height?
- Are the extra structural changes the preemptive repairs make acceptable for this workload?

## Notes
The insight is a change in when the invariant is enforced rather than in what it is. The structure's ordinary rule — every node between a minimum and a maximum — is kept; what the downward pass adds is a slightly stronger promise about the one node it is about to enter. That promise is what lets each step be local: a node that is guaranteed not full can always accept a key from below, and a node guaranteed above its minimum can always give one up.

The payoff is largest where holding a level is expensive. Structures that live on disk read each node as a page, and a version that must back up either keeps the whole path in memory or reads it again; a version that never backs up keeps a fixed handful of pages whatever the height. The same arithmetic applies to anything else a traversal holds per level while it works.
