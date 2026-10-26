---
object_id: PAT_relay_rust_tcp_streams_bidirectionally_for_transparent_proxying
object_type: pattern
name: Relay Rust TCP Streams Bidirectionally for Transparent Proxying
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
- proxy
- relay
- full-duplex
cross_links:
- rel: related_to
  target_object_id: PAT_choose_rust_io_methods_by_completion_contract
- rel: related_to
  target_object_id: PAT_frame_application_messages_above_rust_tcp_streams
reference:
  source_title: Practical System Programming for Rust Developers
  author: Prabhu Eshwarla
confidence: medium
references: []
variants: []
---

# Relay Rust TCP Streams Bidirectionally for Transparent Proxying

## Pattern Rule
**IF** a Rust proxy is meant to be transport-transparent between a client TCP stream and an upstream TCP stream
**THEN** relay bytes in both directions until each direction reaches its own completion boundary, preserving TCP's full-duplex stream behavior
**ELSE** terminate and parse the application protocol at the proxy when inspection, transformation, routing, caching, or message-aware behavior is required

## Do
- Establish one upstream connection for the accepted client connection and treat client-to-upstream and upstream-to-client transfer as independent flows.
- Loop or use a copying primitive that honors the actual number of bytes read and writes all bytes that were produced before reading more.
- Let EOF in one direction end that direction's forwarding without assuming the opposite direction has already finished producing useful data.
- Keep protocol framing out of a transparent relay; if the proxy starts reasoning about messages, make that protocol boundary explicit and use the corresponding framing rules.

## Don't
- Don't implement a generic TCP relay as one `read` followed by one `write` in each direction; neither call represents a complete application conversation.
- Don't assume one side closing its sending direction means no response bytes remain in the reverse direction.
- Don't decode bytes as text merely for forwarding; transparent transport should preserve the byte stream unchanged.

## Checklist
- Is this proxy truly byte-transparent, or does it need application-protocol knowledge?
- Can both directions make progress independently for the lifetime of the connection?
- Are partial reads and writes handled without dropping or duplicating bytes?
- Does one direction's EOF close only the forwarding work that is actually complete?

## Notes
TCP is a full-duplex byte stream. A transparent proxy therefore owns two stream-copy lifecycles, not a single request/read and response/read pair. Once a proxy needs to understand HTTP requests, frame lengths, or another message grammar, it is no longer merely relaying transport bytes and should apply the protocol's own parsing and completion contracts.
