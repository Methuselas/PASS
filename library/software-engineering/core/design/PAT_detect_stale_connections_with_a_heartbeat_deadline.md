---
object_id: PAT_detect_stale_connections_with_a_heartbeat_deadline
object_type: pattern
name: Detect Stale Connections With a Heartbeat Deadline
library_path:
- software-engineering
- core
- design
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: general
specialization_axis: none
foundation_object_id: PAT_check_concurrent_code_for_safety_and_liveness
tags:
- networking
- connections
- liveness
- heartbeats
- timeouts
cross_links:
- rel: related_to
  target_object_id: PAT_block_with_a_deadline_before_polling_on_an_interval
- rel: related_to
  target_object_id: PAT_plan_the_shutdown_early
- rel: related_to
  target_object_id: PAT_specify_the_application_protocol_above_the_transport
reference:
  source_title: Practical Rust Web Projects
  author: Shing Lyu
confidence: medium
references: []
variants: []
---

# Detect Stale Connections With a Heartbeat Deadline

## Pattern Rule
**IF** a long-lived connection can remain apparently open after the peer has stopped responding or making useful progress
**THEN** use explicit liveness evidence with a heartbeat cadence and a separate failure deadline, refresh the deadline only when valid peer evidence arrives, and reclaim the connection after the deadline
**ELSE** when the underlying protocol or platform already provides an adequate bounded liveness guarantee, use that guarantee rather than layering a second heartbeat without a need

## Do
- Keep the heartbeat or probe cadence separate from the deadline that declares the peer stale.
- Refresh the failure deadline only from evidence that demonstrates peer liveness, such as a valid protocol-level response.
- Allow the failure deadline to tolerate transient delay or an isolated missed probe when the service contract permits it.
- Use protocol-native liveness signals when available and stop probes, timers, and normal traffic when the connection closes or is declared stale.
- Choose heartbeat and failure intervals from the service's failure-detection needs and network behavior rather than copying example constants.

## Don't
- Don't treat a successful local send as proof that the peer is alive.
- Don't disconnect on one missed heartbeat by default when transient delay or loss is expected.
- Don't create overlapping uncancelled timers for the same liveness responsibility.
- Don't continue ordinary application work on a connection after its liveness deadline has expired.

## Checklist
- What observation actually proves the peer is alive?
- How often is liveness probed, and what separate deadline declares failure?
- Can one delayed or lost probe cause a false disconnect?
- Are heartbeat timers cancelled when the connection closes?
- Does declaring a connection stale reliably stop normal work and reclaim its resources?

## Notes
A heartbeat is not the timeout itself. The probe creates opportunities for the peer to demonstrate liveness; the independent deadline bounds how long the system will retain a connection without that evidence. Keeping those responsibilities separate prevents both a single delayed response from causing an unnecessary disconnect and an apparently open but dead peer from consuming resources indefinitely.
