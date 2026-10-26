---
object_id: PAT_choose_rust_tcp_or_udp_by_delivery_contract
object_type: pattern
name: Choose Rust TCP or UDP by Delivery Contract
library_path:
- software-engineering
- languages
- rust
- networking
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- rust
- networking
- tcp
- udp
- transport
cross_links:
- rel: related_to
  target_object_id: PAT_frame_application_messages_above_rust_tcp_streams
- rel: related_to
  target_object_id: PAT_treat_rust_udp_connect_as_peer_selection_not_session_establishment
reference:
  source_title: Practical System Programming for Rust Developers
  author: Prabhu Eshwarla
confidence: medium
references: []
variants: []
---

# Choose Rust TCP or UDP by Delivery Contract

## Pattern Rule
**IF** a Rust program must choose between the standard library's TCP and UDP transports for communication between endpoints
**THEN** choose TCP when correctness needs an ordered reliable byte stream, and choose UDP when independent datagrams fit the protocol and any required loss, duplication, ordering, or recovery policy can remain at the application layer

## Do
- Write down whether the application requires a continuous ordered stream or preserves each datagram as an independent unit before choosing `TcpStream` or `UdpSocket`.
- Use TCP when the application should receive bytes in order and rely on the transport to retransmit lost stream data while the connection remains viable.
- Use UDP when datagram boundaries are part of the communication shape and the application can tolerate or explicitly handle loss, duplication, reordering, and retry policy.
- Keep application-message semantics separate from the transport choice; TCP gives a byte stream, while UDP preserves datagram units but does not make them reliable.

## Don't
- Do not choose UDP merely because it appears simpler or lower-overhead when the protocol silently depends on TCP-style reliability or ordering.
- Do not choose TCP and then assume the stream preserves the boundaries of application writes or messages.
- Do not treat transport choice as a substitute for defining application-level failure and retry behavior.

## Checklist
- Does correctness require ordered reliable stream delivery, or are independent datagrams the intended unit?
- If UDP is chosen, where are loss, duplication, ordering, and retry requirements handled?
- If TCP is chosen, where are application-message boundaries defined?

## Notes
Rust exposes these two transport shapes directly through `std::net::TcpStream` and `std::net::UdpSocket`. The API choice should follow the communication contract rather than the surface similarity of their send/read operations.
