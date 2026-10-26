---
object_id: DRILL_handle_framed_tcp_messages_across_partial_io
object_type: drill
name: Handle Framed TCP Messages Across Partial I/O
library_path:
- software-engineering
- languages
- rust
- networking
stage_binding: 2 block
lane_fit: teach
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- rust
- networking
- tcp
- framing
- io
- practice
cross_links:
- rel: teaches
  target_object_id: PAT_frame_application_messages_above_rust_tcp_streams
- rel: teaches
  target_object_id: PAT_choose_rust_io_methods_by_completion_contract
reference:
  source_title: Practical System Programming for Rust Developers
  author: Prabhu Eshwarla
confidence: medium
references: []
variants: []
target_skill: preserving application message boundaries over Rust TCP streams despite
  fragmented, coalesced, and truncated byte delivery
---

# Handle Framed TCP Messages Across Partial I/O

## Practice Task
Implement and test a small length-prefixed Rust protocol over a loopback `TcpStream` so message boundaries remain correct when transport reads and writes do not align with application messages.

## Target Skill
Preserving application message boundaries over Rust TCP streams despite fragmented, coalesced, and truncated byte delivery.

## Setup
Create a small Cargo test project using only the standard library. Use a four-byte big-endian unsigned payload length followed by that many payload bytes, and choose a finite maximum accepted payload length.

## Instructions
1. Implement a frame sender that emits the four-byte length and payload while honoring the write completion contract; record which API or explicit loop guarantees that the complete frame is transferred.
2. Implement a frame receiver that returns one complete payload at a time, treats clean EOF before a new frame as normal stream completion, reports a truncated header or payload as an error, and rejects a declared length above the chosen maximum before allocating that payload.
3. Run a loopback test in which the sender places two encoded frames into one contiguous byte sequence and writes them without waiting for a receive between frames. Record the two payloads the receiver returns.
4. Run a second loopback test in which one encoded frame is deliberately emitted in several small chunks. Record the payload returned after the receiver reassembles the frame.
5. Run a truncation test: send a valid length prefix, send fewer payload bytes than declared, close the sending side, and record the receiver's observed error.
6. Run a clean-completion test that closes the stream between frames and record how the receiver distinguishes that condition from the truncated-frame case.
7. Write down one naive implementation based on one `read` equaling one message, identify which executed test would invalidate it, and state why the failing behavior follows from TCP's stream contract rather than from a timing accident.

## Success Check
- The coalescing test is executed and returns exactly the two original payloads as two frames; merely observing that both byte sequences arrived is the near-miss because it does not prove the framing boundary survived.
- The fragmentation test is executed and returns the original payload even though the encoded frame was sent in multiple chunks; an implementation that equates one `read` with one message would not satisfy both this check and the coalescing check.
- The truncation test produces an observed error while clean EOF between frames produces the receiver's normal end-of-stream result, so premature transport closure cannot masquerade as a valid short message.
- Every frame write uses `write_all` or an explicit count-handling loop, and every fixed-size header/payload read either uses an exact-completion API or proves equivalent count handling; a single unchecked `read` or `write` call fails this check.
- A declared length above the recorded maximum is rejected before payload allocation, and the chosen maximum plus the reason for it are recorded.
- The rejected one-read-per-message implementation names the executed test that disproves it and explains the stream-semantics reason, rather than blaming scheduler timing or local packetization.

## Common Failures
- Using one successful `read` as evidence that a whole application message arrived.
- Testing only one message at a time, which never exposes coalesced-frame handling.
- Treating EOF during a declared frame as if it were the same as clean EOF before the next frame.
- Trusting an unbounded peer-provided length and allocating before applying a protocol limit.

## Notes
The exercise fixes the frame format so the practice target stays narrow: stream framing and transfer completion. Production protocols may use delimiters, varints, structured headers, compression, authentication, timeouts, or async I/O, but those choices do not remove TCP's byte-stream semantics.
