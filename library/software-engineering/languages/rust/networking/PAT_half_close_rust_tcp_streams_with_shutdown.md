---
object_id: PAT_half_close_rust_tcp_streams_with_shutdown
object_type: pattern
name: Half-Close Rust TCP Streams with Shutdown
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
foundation_object_id: PAT_specify_the_application_protocol_above_the_transport
tags:
- rust
- tcp
- shutdown
- half-close
- eof
cross_links:
- rel: related_to
  target_object_id: PAT_specify_the_application_protocol_above_the_transport
reference:
  source_title: Network Programming with Rust
  author: Abhishek Chanda
confidence: high
references: []
variants: []
---

# Half-Close Rust TCP Streams with Shutdown

## Pattern Rule
**IF** a TCP protocol uses end-of-stream in one direction as a meaningful signal while the opposite direction must remain readable
**THEN** call `shutdown(Shutdown::Write)` after the final outbound byte, keep reading until EOF, and reserve a full close for the point when both directions are finished
**ELSE** when the protocol has explicit message framing and no half-close semantics, close the connection only according to that protocol's lifecycle.

## Do
- Use write-side shutdown when the peer must learn that no more request bytes are coming while still being allowed to send a response.
- Continue the local read loop after `Shutdown::Write`; a zero-byte read marks the peer's orderly FIN for that direction.
- Treat the read and write halves as independent protocol states and make their transitions explicit in connection code.
- Use `Shutdown::Both` only when no further inbound or outbound data is valid.

## Don't
- Do not use dropping the `TcpStream` as a substitute for a protocol-required half-close; drop closes the connection rather than preserving the opposite direction.
- Do not treat a zero-byte read as an I/O failure; on a TCP stream it is the EOF signal.
- Do not assume that finishing your writes means the peer has finished its writes.
- Do not depend on platform-specific abortive-close behavior as a framing mechanism; if the peer needs an orderly end signal, send one deliberately.

## Checklist
- Does the protocol use EOF in one direction as part of its message or session contract?
- Is the write half shut down only after the final outbound byte?
- Does the read loop continue until the peer closes its send half?
- Is full connection teardown delayed until both directions are settled?

## Notes
A TCP connection is full duplex. Rust's `Shutdown` enum exposes that directly by allowing read, write, or both halves to be shut down independently. Half-close is therefore a protocol tool, not just resource cleanup: it can communicate "request complete" without discarding a response that is still in flight.
