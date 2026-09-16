---
object_id: PAT_say_which_outside_references_survive_each_operation
object_type: pattern
name: Say Which Outside References Survive Each Operation
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
- references
- handles
- contracts
cross_links:
- rel: related_to
  target_object_id: PAT_define_your_code_contract_explicitly
- rel: related_to
  target_object_id: PAT_keep_a_structure_non_empty_so_the_empty_case_disappears
reference:
  source_title: Introduction to Algorithms
  author: Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, Clifford Stein
confidence: high
references: []
variants: []
---

# Say Which Outside References Survive Each Operation

## Pattern Rule
**IF** code outside a data structure holds references to the elements inside it — a handle kept by the object an element represents, a pointer passed back to an update or delete call, an index remembered for later
**THEN** decide, for every operation, whether those references still refer to the same element afterwards, prefer operations that move links rather than payloads so that they do, and where payloads must move, update the outside references in the same step as the move
**ELSE** where nothing outside the structure ever holds a reference to an element — every access starts from a key and a fresh lookup — elements may be moved and copied freely and the question has no one to answer to.

## Do
- List who holds references into the structure before choosing how its operations rearrange it. The operations that need an element named rather than found — change this element's priority, delete this element — can only be offered cheaply if the caller holds a reference, and that reference is then part of the contract.
- Move links, not payloads, where references must survive. Removing a node that has two children by copying its successor's contents into it and deleting the successor frees a different node from the one the caller named, so anyone still pointing at the successor now points at freed memory; relinking the successor into the removed node's place makes deleting an element delete that element and only that one.
- Keep the back-reference current on every move where elements live in slots that shift. A priority queue held in an array moves an element on every step of every sift, so the application object that remembers its element's position must be told the new position each time it changes; one missed update and a later priority change adjusts the wrong entry.
- Store references in both directions when the operations run both ways. The queue element carries a handle to the application object so the object can be found when it reaches the front; the application object carries a handle to its queue element so its priority can be changed without a search.
- Put the survival rule in the interface. For each operation, say whether references to other elements, to the element operated on, and to positions are still valid afterwards; a caller who has to read the implementation to find out will guess, and the guess fails only on the operations nobody tested.

## Don't
- Don't pick the removal that is simplest to write when callers hold node references. The copy-the-neighbour deletion is shorter and passes every test that only checks which keys remain; it fails only for the caller who kept a pointer, which is the caller the reference-taking interface exists for.
- Don't treat a reference into a contiguous array as stable. Any operation that shifts elements, and any growth that reallocates, moves them; where references must survive such operations, hold an index that is updated on each move, or allocate elements separately and link them.
- Don't search for an element whose reference the caller could have kept. A structure that cannot find an element by identity cheaply — a heap has no efficient search — makes every named-element operation pay for a search unless the reference is held; designing the handle out of the interface moves that cost onto every call.

## Checklist
- Which callers hold references to elements, and which operations do they pass them to?
- For each operation, which references stay valid: to other elements, to the operated-on element, to positions?
- Does any removal or rebalance copy contents between nodes where it could relink them?
- Where elements move between slots, is every outside back-reference updated in the same step?
- Is the survival rule written in the interface rather than left to the implementation?

## Notes
The distinction that matters is between an element's identity and its contents. A structure that keeps each element in one place for its lifetime and changes only the links around it preserves identity through every rearrangement, so references held outside stay meaningful; a structure that shuffles contents between fixed places preserves the set of keys and silently changes what each place holds. Both are correct as sets, and only the first is correct for a caller who holds a reference.

The cost of the named-element operations is where this shows up in practice. Changing an element's priority or deleting a particular element is cheap only if the caller can point at it, and a caller can only point at it if the structure promises the reference survives the operations in between. That promise is design work: it shapes how deletion is written, whether elements live in slots or in separately allocated nodes, and what every move must update — which is why it belongs in the interface rather than being discovered from a stale pointer.
