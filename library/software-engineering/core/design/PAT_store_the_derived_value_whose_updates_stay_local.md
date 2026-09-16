---
object_id: PAT_store_the_derived_value_whose_updates_stay_local
object_type: pattern
name: Store the Derived Value Whose Updates Stay Local
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
- design
- derived_state
- data_structures
- maintenance
- invalidation
cross_links:
- rel: related_to
  target_object_id: PAT_give_knowledge_one_authoritative_home
- rel: related_to
  target_object_id: PAT_choose_lazy_or_eager_by_how_often_the_result_is_needed
- rel: related_to
  target_object_id: PAT_choose_the_data_structure_for_the_dominant_access_pattern
reference:
  source_title: Introduction to Algorithms
  author: Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, Clifford Stein
confidence: high
references: []
variants: []
---

# Store the Derived Value Whose Updates Stay Local

## Pattern Rule
**IF** you have decided to store a value that could instead be recomputed — a count held on a parent, an aggregate on a node, a bounding volume, a running total
**THEN** among the formulations that answer the questions you need answered, choose the one whose value at any point is computable from that point and its immediate neighbours, so a change to the underlying data travels a short and bounded distance
**ELSE** where every candidate formulation requires touching the whole structure on an update, store nothing and compute on demand — the query cost is the honest price of not maintaining it.

## Do
- Settle what an update costs before settling what the query buys, because that order is what makes the design converge. Choosing the stored value and building new queries on it is wasted effort if the value cannot then be kept current cheaply, and that is the step most likely to fail.
- Test each candidate by what its definition mentions. A value defined in terms of a node and its immediate children can be repaired by recomputing it at the point of change and then at each ancestor in turn, which is one short walk. A value defined in terms of the whole structure offers no such chain, so there is nothing to walk and the repair is a full pass.
- Compare formulations that answer the identical query, because they are rarely equally maintainable and the difference is easy to miss. Storing each element's position in the overall order and storing the size of each subtree both answer "what sits at position k" quickly. Inserting a new smallest element changes the first at every single node and the second only along one path. The queries are indistinguishable; the maintenance costs differ by the size of the structure.
- Enumerate every operation that can invalidate the value, including the ones that change no data at all. Rebalancing, splitting, merging and reparenting move things around without altering a single underlying value, and a derived field that is correctly maintained under insertion and removal can still be wrong immediately after a rotation.
- Prefer a formulation that composes from its parts over one that is merely correct. A value each node computes from its children's values of the same kind extends to new operations for free, because any operation that repairs the parent-child relation repairs the value too.
- Keep the maintenance in the same place as the operation that disturbs it. A derived value updated by callers rather than by the structure that owns it is one that goes stale the first time somebody adds a path nobody remembered.

## Don't
- Don't choose the formulation that makes the query read most naturally. The query is written once and the maintenance runs on every modification, so a slightly more awkward stored quantity with local updates is the better trade nearly every time.
- Don't assume a value that is cheap to maintain under one operation is cheap under all of them. Cheap under append and ruinous under insert-at-front is a common shape, and the operation that is expensive is often the one added later.
- Don't store a derived value whose update cost you have not written down somewhere. The cost is invisible at every call site — each individual update looks like one assignment — and only becomes apparent as a whole when the structure is large.
- Don't reach for this before establishing that the value needs storing at all. Whether to hold a derived value, and how to contain it once you do, is a separate and prior decision that `PAT_give_knowledge_one_authoritative_home` owns; this one only picks between formulations after that decision has gone in favour of storing something.

## Checklist
- Which operations change the underlying data, and how far does each one's effect on the stored value reach?
- Is the stored value definable from a point and its immediate neighbours, or only from the structure as a whole?
- Is there a second formulation that answers the same queries with a shorter propagation path?
- Do the structural operations — rebalancing, merging, moving — also maintain it, or only the data-changing ones?
- Has the update cost been written down anywhere a reader would find it?

## Notes
The reason this is worth stating separately from the general caution about derived state is that it is a choice between candidates rather than a warning against a practice. Everyone knows a cached value must be kept current; far fewer treat the *shape* of the cached value as a decision with a large cost attached. Two quantities can be exactly equivalent in what they let you ask and differ by a factor of the structure's size in what they cost to keep honest, and nothing in the query code hints at the difference.

The locality test generalises well past the tree case that makes it easiest to see. A count held on a parent row, a bounding volume on a scene-graph node, a running subtotal on a group, a dirty flag propagated toward a root — each is maintainable exactly to the extent that its value is a function of the immediate children's values, and each becomes a whole-structure sweep when it is instead defined against some global fact like an absolute position or a rank among everything.

The failure that catches people is the structural operation. Insertion and removal are obvious candidates for breaking a derived value and get handled; rebalancing is not, because it changes no underlying data and feels like bookkeeping beneath the level anyone is reasoning about. A formulation whose value each node computes from its children survives it automatically, since repairing the relation repairs the value. A formulation defined globally does not, and the resulting defect appears only on inputs that happen to trigger a rotation.
