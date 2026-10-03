---
object_id: PAT_end_rust_channel_consumption_by_dropping_every_sender
object_type: pattern
name: End Rust Channel Consumption by Dropping Every Sender
library_path: [software-engineering, languages, rust, concurrency]
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: PAT_separate_buffer_ownership_from_message_delivery
tags: [rust, concurrency, channels, ownership, shutdown]
cross_links:
- rel: related_to
  target_object_id: PAT_plan_the_shutdown_early
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
references: []
variants: []
---

# End Rust Channel Consumption by Dropping Every Sender

## Pattern Rule
**IF** one or more Rust producers send owned values to a consumer over a channel
**THEN** move each value through `send`, clone the sender only for genuine producers, and make dropping every sender the explicit end-of-stream signal
**ELSE** use shared state when participants must observe and modify one current value rather than transfer independent messages.

## Do
- Treat a successful `send(value)` as an ownership transfer; continue using the value only if it was deliberately cloned before sending.
- Clone the sending endpoint for each producer that needs one, and keep the receiving endpoint with the consumer.
- Drop each producer's sender when that producer is finished, including spare senders retained by setup code.
- Let blocking receive or receiver iteration terminate when every sender has been dropped, and handle disconnection as a normal lifecycle event when it represents completion.
- Use nonblocking receive only when the consumer has other useful work or scheduling responsibilities between polls.

## Don't
- Don't retain an unused sender while waiting for receiver iteration to end; that sender keeps the channel open forever.
- Don't use message passing as if it were shared memory. The receiver owns each received value unless the message itself contains shared ownership.
- Don't ignore a send error; it means the receiver has gone away and the message could not be delivered.
- Don't busy-poll a nonblocking receive when a blocking wait would express the consumer's real behavior.

## Checklist
- Which producer owns each sender clone?
- Is the message intentionally moved, or must the producer keep an independent copy?
- Who drops the last sender, and on every exit path?
- Does disconnection mean successful completion, cancellation, or failure here?
- Should the consumer block, iterate, or poll while waiting?

## Notes
Rust channels connect concurrency lifecycle to ownership. Sending normally moves the message, preventing the producer from mutating the same value after transfer. The receiver learns that no more messages can arrive only when all sending endpoints are gone, so sender ownership is also the channel's shutdown protocol. A forgotten clone is therefore not just a leak of a small handle; it is a consumer that may wait forever.
