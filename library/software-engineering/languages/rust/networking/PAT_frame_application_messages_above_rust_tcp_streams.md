---
object_id: PAT_frame_application_messages_above_rust_tcp_streams
object_type: pattern
name: Frame Application Messages Above Rust TCP Streams
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
- tcp
- protocols
- framing
cross_links:
- rel: related_to
  target_object_id: PAT_choose_rust_io_methods_by_completion_contract
- rel: related_to
  target_object_id: PAT_choose_rust_tcp_or_udp_by_delivery_contract
reference:
  source_title: Practical System Programming for Rust Developers
  author: Prabhu Eshwarla
confidence: medium
references: []
variants: []
---

# Frame Application Messages Above Rust TCP Streams

## Pattern Rule
**IF** a Rust application carries discrete protocol messages over `TcpStream`
**THEN** define an application-level framing rule and accumulate or emit bytes according to that rule instead of treating one TCP read or write call as one complete message

## Do
- Choose a framing rule the protocol can observe, such as a fixed size, a length prefix, a delimiter, or protocol-defined headers that determine the body length.
- Accumulate only the bytes actually returned by `read` until the framing rule says a complete message is present, then parse that complete frame.
- When forwarding a frame, write only the bytes that belong to it and use the I/O completion contract required to finish that frame.
- Preserve any bytes beyond one complete frame for the next message rather than discarding or misattributing them.

## Don't
- Do not equate one successful `read` with one complete request or response.
- Do not parse or forward the unused tail of a fixed-capacity buffer as though it came from the network.
- Do not assume one sender-side write produces one receiver-side read of the same size.

## Checklist
- What observable rule marks the end of one application message?
- Can one message arrive across several reads, or several messages arrive in one read?
- Does every parse and forward step use exactly the bytes belonging to the current frame?
- What happens to bytes already read that belong to the following frame?

## Notes
TCP provides an ordered byte stream but does not preserve application-message boundaries. Framing is therefore a protocol decision above `TcpStream`; Rust's partial-I/O rules are a separate lower-level contract that the framing implementation must also honor.
