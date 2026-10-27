---
object_id: PAT_correlate_multiplexed_requests_with_explicit_ids
object_type: pattern
name: Correlate Multiplexed Requests With Explicit IDs
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
- protocols
- multiplexing
- correlation
- request-response
cross_links:
- rel: related_to
  target_object_id: PAT_specify_the_application_protocol_above_the_transport
- rel: related_to
  target_object_id: PAT_dispatch_on_readiness_or_on_completion
reference:
  source_title: Network Programming with Rust
  author: Abhishek Chanda
confidence: medium
references: []
variants: []
---

# Correlate Multiplexed Requests With Explicit IDs

## Pattern Rule
**IF** one connection or channel can carry multiple requests concurrently and responses may complete in a different order from submission
**THEN** put an explicit correlation identifier in the protocol envelope and use it to match each response to the outstanding request it completes
**ELSE** when the protocol guarantees at most one outstanding request or strict ordered pairing, the ordering contract itself can supply the association

## Do
- Choose identifiers that are unique among all requests that can still produce a response.
- Carry the identifier through the request/response envelope without making application business data responsible for transport correlation.
- Keep an explicit mapping from correlation identifier to pending request state while it is active, then retire or tombstone it according to the protocol's late-response and identifier-reuse policy.
- Define what happens to unknown, duplicate, late, or already-retired identifiers as part of the protocol contract.

## Don't
- Don't pair replies to requests by arrival order once concurrent operations can finish out of order.
- Don't reuse an identifier while an earlier request with that identifier can still produce a response.
- Don't bury correlation in a business field whose meaning or uniqueness is controlled by the application payload.

## Checklist
- Can more than one request be outstanding on this connection or channel?
- Can responses arrive in a different order from requests?
- Where is the correlation identifier encoded and how long is it reserved?
- What retires the pending mapping, and how are late or unknown responses handled?

## Notes
When multiplexing permits out-of-order completion, submission order no longer identifies which request a response completes. The correlation identifier restores that relationship without forcing independent work back into serialized request/response order.
