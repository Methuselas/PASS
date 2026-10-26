---
object_id: PAT_treat_rust_udp_connect_as_peer_selection_not_session_establishment
object_type: pattern
name: Treat Rust UDP Connect as Peer Selection, Not Session Establishment
library_path:
- software-engineering
- languages
- rust
- networking
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- rust
- networking
- udp
- sockets
- api-contracts
cross_links:
- rel: related_to
  target_object_id: PAT_choose_rust_tcp_or_udp_by_delivery_contract
reference:
  source_title: Practical System Programming for Rust Developers
  author: Prabhu Eshwarla
confidence: medium
references: []
variants: []
---

# Treat Rust UDP Connect as Peer Selection, Not Session Establishment

## Pattern Rule
**IF** a Rust UDP socket should communicate repeatedly with one remote endpoint
**THEN** use `UdpSocket::connect` to select that peer for `send` and `recv` and to restrict received traffic to that address, while continuing to treat UDP as connectionless rather than as an established reliable session

## Do
- Use `connect` when one UDP peer is the intended default destination and source for the socket.
- Use `send_to` and `recv_from` when the socket intentionally communicates with multiple peers or the sender address is part of each datagram's handling.
- Treat a successful UDP `connect` as successful local peer selection; determine remote reachability and application liveness through subsequent communication and the protocol's own acknowledgments when needed.
- Keep reliability, ordering, duplicate handling, and retry policy independent of whether the UDP socket is connected.

## Don't
- Do not describe successful `UdpSocket::connect` as proof that a remote server is listening or that a handshake completed.
- Do not infer TCP-style session, ordering, or reliability guarantees from using `send` and `recv` on a connected UDP socket.
- Do not use connected-UDP convenience to hide a requirement to receive legitimate datagrams from multiple peers.

## Checklist
- Is one remote endpoint the intended peer for this socket?
- Does any code treat `connect` success as evidence that the remote application accepted a session?
- Would filtering received datagrams to this peer discard traffic the application actually needs?
- Where are reliability and liveness established if the application requires them?

## Notes
`UdpSocket::connect` changes the local socket's peer-selection behavior and enables the connected forms of datagram I/O. It does not change UDP's transport semantics into those of TCP.
