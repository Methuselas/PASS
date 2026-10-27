---
object_id: PAT_choose_transport_by_delivery_contract
object_type: pattern
name: Choose a Transport by the Delivery Contract
library_path:
- software-engineering
- core
- design
stage_binding: 0 design
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- networking
- transport
- tcp
- udp
- delivery-contract
cross_links: []
reference:
  source_title: Network Programming with Rust
  author: Abhishek Chanda
confidence: medium
references: []
variants: []
---

# Choose a Transport by the Delivery Contract

## Pattern Rule
**IF** you are choosing how application messages should be transported across a network
**THEN** state the delivery contract first—ordering, reliability, byte-stream versus datagram boundaries, communication fan-out, setup cost, and tolerance for loss or reordering—and choose the transport whose native semantics satisfy that contract
**ELSE** when the native transport does not provide the full contract, add the missing framing or reliability explicitly at a higher protocol layer rather than assuming the transport supplies it

## Do
- Treat TCP as a connection-oriented ordered byte stream whose reliability and congestion behavior come with connection state and setup.
- Treat UDP as independent datagrams with no transport guarantee that a datagram is delivered or delivered in order; add higher-layer reliability only when the application contract requires it.
- Include communication shape in the contract: point-to-point traffic leaves more transports available, while native IP multicast or IPv4 broadcast requires datagram-style group delivery rather than one connection per receiver.
- Make correctness of the delivery contract the first filter; compare header or setup overhead only after the required semantics are explicit.

## Don't
- Don't choose UDP merely because its header or setup is smaller when the application actually requires reliable ordered delivery.
- Don't infer application-message boundaries from a TCP connection; a byte stream and a message protocol are different layers.
- Don't treat a protocol layered over UDP as inherently unreliable; the higher layer can deliberately supply reliability or ordering.

## Checklist
- What loss, duplication, and reordering can the application tolerate?
- Does the application need a byte stream or preserved datagram boundaries?
- Is delivery point-to-point, one-to-many, or group-addressed?
- Is connection setup/state acceptable for the interaction pattern?
- If the transport omits a required property, which higher layer owns it?

## Notes
TCP and UDP are service contracts, not generic 'reliable versus fast' labels. Choose from the behavior the application needs, then make any missing message framing or reliability a deliberate protocol responsibility.
