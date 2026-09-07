---
object_id: PAT_augment_a_structure_with_locally_derivable_data
object_type: pattern
name: Augment a Structure With Locally Derivable Data
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
- data_structures
- design
- maintainability
cross_links:
- rel: related_to
  target_object_id: PAT_choose_a_problem_representation_before_solving
- rel: related_to
  target_object_id: PAT_update_a_sliding_computation_incrementally
reference:
  source_title: 'Introduction to Algorithms, 3rd Edition'
  author: Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, Clifford Stein
confidence: high
references: []
variants: []
---

# Augment a Structure With Locally Derivable Data

## Pattern Rule
**IF** an existing data structure already supports the operations you need but not the query you have just been asked to add, and rewriting or replacing the structure would cost more than extending it
**THEN** add the new information as an attribute derivable from a node's own data and its immediate children, verify that a single change only forces updates along the path from that change to wherever nothing further depends on it, and build the new query on top of that attribute — rather than adding something that requires touching every element to keep current
**ELSE** where the information needed cannot be computed from anything local — it genuinely depends on the whole structure's shape in a way no single change confines — augmenting is the wrong move, and a different structure or a full recomputation is the honest one.

## Do
- Separate four decisions and make each one before the next: which existing structure to build on, what additional attribute to store, whether that attribute survives every mutation the structure already supports at no extra asymptotic cost, and what new operation the attribute now makes possible. Skipping to the new operation before checking the third decision is how an elegant idea turns out to be unmaintainable.
- Prefer an attribute whose value at any point is a function of that point's own data and its immediate children's already-computed attributes. That locality is what confines the cost of one change to the path from the change up to wherever the dependency stops, rather than spreading it across the whole structure.
- Verify the maintenance cost against the structure's own existing bound, not against zero. An attribute recomputable in the same time the structure's own rebalancing already takes is free; one that costs more has undone the reason the structure was chosen in the first place.
- Check what a purely structural change does to the attribute, not only what a value change does. A tree's rebalancing moves nodes around without changing any key, and the attribute has to be recomputed correctly across that move too, not only across ordinary insertion and deletion.

## Don't
- Don't store a global quantity — a node's absolute rank across the whole structure, its distance from one fixed point — directly at every node. A change near one end then forces an update at every other node, which defeats the entire purpose of augmenting rather than rebuilding; store something local from which the global quantity can still be derived within the time the query can afford.
- Don't design the new operation before confirming the attribute survives mutation. An operation built against an attribute that turns out too expensive to maintain is a plan for a structure that cannot be built at the complexity it promised.
- Don't treat augmenting as "just adding a field." The field carries a maintenance obligation for the life of the structure, and that obligation is the entire cost of the technique — a field nobody keeps current is worse than no field, since it looks trustworthy and isn't.

## Checklist
- Which existing operations would have to touch this attribute, and how many nodes would each one touch?
- Can the attribute be computed from a node's own data plus its immediate children, or does it need something farther away?
- Does maintaining it under every mutation the structure supports — rebalancing included — stay within that structure's existing time bound?
- Has the new operation actually been built on the attribute, or does the design stop at "we could add a field for that"?

## Notes
This is worth keeping distinct from choosing a data structure in the first place. Choosing decides which structure's baseline operations fit the dominant access pattern; augmenting decides how far an already-chosen structure can be stretched to answer a new question without abandoning it. The two are sequential, not competing — augmenting only becomes the right move once a structure has already been chosen for reasons that have nothing to do with the new query.

The locality requirement is the load-bearing idea and generalizes past any one structure: whenever a derived value can be written as a small function of a handful of neighbors, maintaining it costs about what maintaining those neighbors already costs; whenever it can't, no amount of bookkeeping keeps the cost from spreading across the whole structure on every change.
