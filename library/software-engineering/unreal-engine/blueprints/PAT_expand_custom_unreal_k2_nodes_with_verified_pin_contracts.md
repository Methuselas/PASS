---
object_id: PAT_expand_custom_unreal_k2_nodes_with_verified_pin_contracts
object_type: pattern
name: Expand Custom Unreal K2 Nodes with Verified Pin Contracts
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- k2_nodes
- compiler
- graph_expansion
cross_links:
- rel: related_to
  target_object_id: PAT_shape_blueprint_function_nodes_for_graph_use
- rel: related_to
  target_object_id: PAT_cross_unreal_blueprint_wildcards_with_reflection_safe_thunks
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Expand Custom Unreal K2 Nodes with Verified Pin Contracts

## Pattern Rule
**IF** a custom `UK2Node` compiles by replacing itself with intermediate nodes
**THEN** treat its pins, wildcard propagation and expansion graph as a compiler contract, validate every connection as it is created, and finish only when all user links have moved to a type-correct supported graph.

## Do
- Give every pin a stable internal name, explicit direction and deliberate allocation order. Keep friendly labels separate from identifiers used by reconstruction and compilation.
- Serialize only the minimum state needed to reconstruct dynamic pin types. On connect, derive all dependent wildcard types from the authoritative input; on disconnect or unlinked paste, restore the entire dependent set coherently.
- Register the node through the Blueprint action database and provide category, title and tooltip text that states the operation rather than its expansion mechanics.
- Sketch and test the intended intermediate graph before encoding it. Spawn nodes through `FKismetCompilerContext`, configure function/type state before `AllocateDefaultPins`, and retrieve pins through checked accessors.
- Distinguish moving an existing user link, copying it to multiple consumers and creating a new internal link. Check every `FPinConnectionResponse`, include source/destination identity in compiler diagnostics and stop expansion after a failed required connection.
- Set wildcard types before connecting nodes that cannot infer them; for nodes that do infer, connect in a documented order and verify no required pin remains wildcard.
- Set defaults through the schema or an equivalently validated helper so type and literal syntax agree.
- At the end, assert that every original link was transferred intentionally, break no unexplained remainder, and report a compile error rather than silently discarding a connection.
- Test reconstruction, undo/redo, copy/paste, load after editor restart, disconnect/reconnect, invalid types, empty inputs and compile after an engine upgrade.

## Don't
- Don't use `BreakAllNodeLinks()` to hide an incomplete expansion.
- Don't assume the order of connection creation is irrelevant when wildcard callbacks depend on it.
- Don't claim runtime speed from a K2 node whose C++ runs only while compiling the Blueprint.
- Don't hand-author bytecode when an expansion into supported nodes provides equivalent behavior and better compiler integration.

## Checklist
- Can the node reconstruct the same pin types after save/load, paste and undo?
- Does each expansion link identify whether it moves, copies or creates connectivity?
- Are compiler failures localized to the exact pin operation that violated the schema?
- Are all original pins disconnected only because their links were accounted for?

## Notes
A custom K2 node is a source-language feature implemented by a compiler lowering. Its primary correctness test is equivalence between the visible node contract and the expanded graph, not the amount of C++ used to build it.
