---
object_id: PAT_respect_datagram_boundaries_in_rust_udp
object_type: pattern
name: Respect Datagram Boundaries in Rust UDP
library_path: [software-engineering, languages, rust, networking]
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, networking, udp, datagram, recv_from, buffer_size]
cross_links:
- rel: related_to
  target_object_id: PAT_choose_rust_tcp_or_udp_by_delivery_contract
- rel: related_to
  target_object_id: PAT_choose_rust_io_methods_by_completion_contract
- rel: related_to
  target_object_id: PAT_treat_rust_udp_connect_as_peer_selection_not_session_establishment
reference: {source_title: Practical System Programming for Rust Developers, author: Prabhu Eshwarla}
confidence: medium
references: []
variants: []
---

# Respect Datagram Boundaries in Rust UDP

## Pattern Rule
**IF** Rust code receives application data with `UdpSocket`
**THEN** treat each receive as one datagram, use the returned byte count as that datagram's content boundary, and size or frame messages so an undersized receive buffer cannot silently violate the application contract.

## Do
- Slice the receive buffer to the count returned by `recv_from` or `recv`; bytes beyond that count are not part of the datagram just received.
- Preserve datagram semantics in the application design: separate sends remain separate datagrams, and UDP does not create a continuous byte stream for the receiver to reassemble implicitly.
- Set the receive-buffer size from the largest datagram the protocol permits, or add application-level chunking/reassembly when messages can exceed that bound.
- Handle receive errors per datagram and continue the server loop when policy allows; one malformed or oversized packet should not take down unrelated clients.
- When handing a received datagram to another thread or task, move an owned exact-length copy or another ownership-safe representation rather than relying on reuse of the mutable receive buffer.

## Don't
- Don't echo or parse the entire backing array after a short receive; unused bytes may be zeros or residue from previous receives.
- Don't assume send success proves the peer received the datagram intact.
- Don't apply TCP stream framing assumptions to UDP; message boundaries already exist at the datagram layer, while reliability and multi-datagram reassembly remain application concerns.

## Checklist
- Is every buffer use bounded by the returned receive count?
- Is the receive buffer large enough for the protocol's largest single datagram?
- If larger logical messages exist, where are chunk numbering and reassembly defined?
- Does a receive error stay local to that datagram when the server can continue?
- Does asynchronous handling own the bytes it processes?

## Notes
The source UDP server already receives `(num_bytes, src_addr)` and slices to `buffer[..num_bytes]`. That count is part of the protocol boundary. The durable distinction from TCP is that UDP preserves datagram units but does not supply reliability, ordering, or automatic reconstruction of messages split across several datagrams.
