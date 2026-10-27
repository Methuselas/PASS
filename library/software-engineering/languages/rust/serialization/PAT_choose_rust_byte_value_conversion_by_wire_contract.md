---
object_id: PAT_choose_rust_byte_value_conversion_by_wire_contract
object_type: pattern
name: Choose Rust Byte-Value Conversion by the Wire Contract
library_path:
- software-engineering
- languages
- rust
- serialization
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: PAT_compose_parsers_from_small_rules
tags:
- rust
- serde
- serialization
- parsing
- wire-format
- protocol
cross_links:
- rel: related_to
  target_object_id: PAT_compose_parsers_from_small_rules
- rel: related_to
  target_object_id: PAT_specify_the_application_protocol_above_the_transport
reference:
  source_title: Network Programming with Rust
  author: Abhishek Chanda
confidence: high
references: []
variants: []
---

# Choose Rust Byte-Value Conversion by the Wire Contract

## Pattern Rule
**IF** Rust code must convert between typed values and an external byte or text representation
**THEN** first ask whether that wire format maps cleanly through Serde's data model and has a maintained serializer or deserializer; use Serde when it does, and use an explicit parser or codec when the protocol's grammar, state, bit layout, or streaming rules are the real contract
**ELSE** for an internal representation with no external compatibility requirement, choose the simplest maintained format that satisfies storage and interoperability needs.

## Do
- Derive `Serialize` and `Deserialize` for ordinary Rust data structures when a maintained Serde format implementation already defines the required wire representation.
- Customize Serde through attributes or explicit trait implementations when the wire representation still fits the Serde data model but the default derive shape is insufficient.
- Build an explicit parser or codec when the external protocol is defined as a grammar, state machine, fixed bit layout, or incremental stream that does not naturally map through an existing Serde format.
- Keep framing separate from conversion. A decoder should receive one complete protocol unit or an explicit streaming input contract rather than assuming one socket read equals one value.
- For explicit binary parsing, honor the specification's byte order, field widths, and incomplete-input behavior rather than native integer layout.

## Don't
- Do not reject Serde merely because the format is externally specified; JSON, TOML, CBOR, and many other external formats have Serde implementations precisely for that case.
- Do not force a protocol with stateful grammar or bit-level layout through an artificial struct solely to reuse derive macros.
- Do not invent a second bespoke encoder when a maintained Serde format already matches the interoperability contract.
- Do not let transport chunking define value boundaries.

## Checklist
- Does a maintained Serde format implementation match the actual wire contract?
- Can the required representation be expressed by derive, attributes, or a custom Serde implementation without obscuring the protocol?
- Does the format instead require grammar composition, incremental parsing, or exact bit and byte layout?
- Is framing or stream completeness settled before conversion begins?

## Notes
Serde separates Rust data structures from data formats through a common data model, so "external format" and "Serde" are not opposites. Parser combinators solve a different problem: recovering structure from a grammar or byte protocol whose boundaries and states are themselves part of the specification. Choose between them from the wire contract, then keep either choice above the transport and framing layers.
