---
object_id: PAT_generate_rpc_bindings_from_one_service_schema
object_type: pattern
name: Generate RPC Bindings From One Service Schema
library_path:
- software-engineering
- core
- hard-to-misuse
stage_binding: 0 design
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- rpc
- idl
- schema
- code-generation
- contracts
cross_links:
- rel: related_to
  target_object_id: PAT_single_source_of_truth_for_logic
- rel: related_to
  target_object_id: PAT_describe_data_by_meaning_when_it_leaves_the_machine
reference:
  source_title: Network Programming with Rust
  author: Abhishek Chanda
confidence: medium
references: []
variants: []
---

# Generate RPC Bindings From One Service Schema

## Pattern Rule
**IF** independently built RPC clients and servers must agree on operation names and structured request and response messages, and the toolchain supports a shared machine-readable service contract
**THEN** put that contract in one schema or interface definition and generate endpoint bindings from it
**ELSE** keep one authoritative RPC contract and implement the endpoint adapters explicitly rather than maintaining independent copies of the operations and message shapes

## Do
- Define service operations and request and response message fields in the shared contract before generating endpoint code.
- Generate both client-facing and server-facing bindings from the same authoritative definition.
- Regenerate endpoint bindings when the contract changes instead of hand-editing generated artifacts.
- Keep application behavior in handwritten code and keep generated schema/transport plumbing replaceable.

## Don't
- Don't duplicate request, response, or operation definitions independently in every client and server implementation.
- Don't treat generated stubs as the authoritative contract when the schema that produced them is available.
- Don't place business logic in generated files that regeneration can overwrite.

## Checklist
- Is there one authoritative definition of service operations and message shapes?
- When code generation is available, are all supported endpoint bindings generated from that same definition?
- Can generated bindings be regenerated reproducibly when the contract changes?
- Are generated files separated from handwritten service behavior?

## Notes
The durable idea is contract-driven generation, not any particular RPC framework or schema language. A machine-readable interface definition makes endpoint agreement executable instead of relying on independently maintained copies.
