---
object_id: PAT_keep_a_structural_invariant_loose_enough_to_repair_locally
object_type: pattern
name: Keep a Structural Invariant Loose Enough to Repair Locally
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
- invariants
- balancing
- design_tradeoffs
cross_links:
- rel: related_to
  target_object_id: PAT_keep_a_spare_before_releasing_capacity
- rel: related_to
  target_object_id: PAT_bound_the_sequence_when_one_operation_is_occasionally_expensive
- rel: related_to
  target_object_id: PAT_repair_on_the_way_down_so_one_pass_never_backs_up
reference:
  source_title: Introduction to Algorithms
  author: Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, Clifford Stein
confidence: high
references: []
variants: []
---

# Keep a Structural Invariant Loose Enough to Repair Locally

## Pattern Rule
**IF** a structure keeps a shape invariant so that its operations stay fast — a height bound, an occupancy bound, a balance condition — and every insertion or deletion can disturb it
**THEN** state the invariant as the weakest condition that still delivers the bound you need, with a range wide enough that one disturbance can be repaired by a bounded amount of local work, instead of the exact ideal shape that a single change can push out of place everywhere
**ELSE** where the structure is built once and never modified, the exact shape costs nothing to maintain and gives the best constant.

## Do
- Start from the bound the operations need, not from the ideal shape. Logarithmic height needs only that no root-to-leaf path is more than a constant factor longer than any other; it does not need every level full. A tree whose longest path is at most twice its shortest has height at most twice the logarithm of its size, and that is enough.
- Check that the slack absorbs one operation's disturbance with local repairs. With the twice-as-long rule, an insertion is repaired by recolouring that moves upward and at most two rotations, and a deletion by at most three; the repair touches a path, never the whole tree.
- Make an occupancy range at least wide enough that the repair of one boundary produces legal pieces on the other side. Nodes allowed anywhere from half full to full can split a full node into two half-full nodes around a median, and can merge two minimal nodes and the key between them into one full node; a range narrower than that would make a split produce nodes that are already illegal.
- Allow a bounded amount of damage before repairing it. A heap whose trees may be cut apart lets a node lose one child with no repair at all and cuts the node loose only when it loses a second; that single spare is enough to keep every subtree's size exponential in its root's degree, and it keeps the cost of changing a key constant amortized, where cutting on the first loss would cascade on every change.
- Price the slack in space and in the constant. A looser invariant means nodes may sit half empty and paths may be up to twice the shortest; tightening the minimum occupancy saves space and buys more frequent repair, and that trade is the design parameter.
- Apply the same move to capacity that grows and shrinks. Separate thresholds for growing and shrinking are this rule applied to a count rather than a shape, and they fail for the same reason when the gap is zero.

## Don't
- Don't maintain the ideal shape because it is the easiest to describe. A tree kept perfectly balanced has no slack, so one insertion at the wrong place can force nodes throughout the tree to move to restore it, and that cost lands on the operation the invariant was meant to keep fast.
- Don't loosen past the bound. The range is chosen from what the operations need; an invariant loose enough to allow a path linear in the size has stopped guaranteeing anything.
- Don't let two thresholds meet. A split that produces a node at exactly the merge threshold, or a grow condition equal to the shrink condition, lets alternating operations trigger a repair every time.

## Checklist
- What bound do the operations actually need — height, occupancy, load — and what is the weakest invariant that implies it?
- How much work does repairing one insertion or one deletion take under that invariant, and is it local?
- Does repairing one boundary produce pieces that are legal against the opposite boundary?
- What does the slack cost in space and in the constant, and is that the right trade for this workload?
- Is there a gap between the thresholds, so a single alternating operation cannot trigger repair each time?

## Notes
The underlying trade is between how good the shape is and how cheaply it can be kept. An exact invariant has no room, so the smallest disturbance is already a violation and its repair can spread as far as the shape extends. A relaxed invariant gives up a constant factor in the quality of the shape — paths up to twice as long, nodes as little as half full — and in return a disturbance lands inside the permitted range or just outside it, where a local repair brings it back. The bound survives because it depended only on the relaxed condition all along.

The occupancy case shows why the width of the range matters, not just its existence. Splitting and merging are the two local repairs, and each has to produce nodes that are legal immediately; that fixes the minimum at no more than half the maximum. A structure that wants denser nodes can raise the minimum — one variant requires nodes to be two-thirds full — but then splitting one full node in half produces two nodes below the new minimum, so the repair can no longer be confined to the node that overflowed.
