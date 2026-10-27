---
object_id: PAT_bound_blocking_rust_socket_io_with_timeouts
object_type: pattern
name: Bound Blocking Rust Socket I/O with Timeouts
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
- blocking
- timeout
- io
cross_links:
- rel: related_to
  target_object_id: PAT_choose_transport_by_delivery_contract
reference:
  source_title: Network Programming with Rust
  author: Abhishek Chanda
confidence: high
references: []
variants: []
---

# Bound Blocking Rust Socket I/O with Timeouts

## Pattern Rule
**IF** a Rust program uses blocking sockets for operations whose wait time must be bounded by the application
**THEN** apply explicit connect, read, and write time limits at the socket boundary, classify timeout separately from peer closure and protocol failure, and give every retry path its own budget
**ELSE** when indefinite blocking is an intentional part of a dedicated-thread design, document that contract rather than inheriting it accidentally from the operating system.

## Do
- Use `TcpStream::connect_timeout` when one resolved socket address must have a bounded dial attempt. When a hostname resolves to several addresses, resolve first and apply the connection policy to each candidate rather than assuming one timeout covers the whole name.
- Set read and write timeouts on each established `TcpStream` when a silent peer must not occupy the caller indefinitely.
- Treat timeout errors as platform-sensitive: Unix commonly reports `WouldBlock`, while Windows may report `TimedOut`. Classify by the documented timeout contract instead of one hard-coded operating-system error value.
- Keep timeout, retry, and overall deadline separate. A three-second read timeout repeated forever is still an unbounded operation.
- Interpret a timed-out read as "no progress within this window," not as EOF. A zero-byte read is the orderly stream-closure signal.

## Don't
- Do not rely on a platform's default TCP retry timers when the product has a shorter responsiveness requirement.
- Do not tear down a live connection solely because one read window expired when the application protocol permits idle gaps.
- Do not treat a completed write as proof the peer consumed the bytes; the call only reports local write progress under the socket contract.
- Do not loop on timeout without a retry count, deadline, cancellation signal, or other terminal condition.

## Checklist
- Is dialing bounded independently from reads and writes after connection?
- Can the error path recognize both Unix-style `WouldBlock` and Windows-style `TimedOut` timeout results?
- What is the retry budget or overall deadline above the per-operation timeout?
- Does the protocol say whether an idle read window is recoverable or terminal?

## Notes
Blocking network calls are useful precisely because they make one thread wait for one operation, but that simplicity should not silently decide latency policy. Rust exposes a connect timeout separately from the per-stream read and write timeouts, and the timeout error kind is intentionally platform-specific. The durable rule is therefore to bound waits at the application boundary and interpret them according to the protocol, not to key behavior to one errno.
