---
object_id: PAT_scale_rust_tcp_accept_across_cores_with_reuseport_listeners
object_type: pattern
name: Scale Rust TCP Accept Across Cores with ReusePort Listeners
library_path:
- software-engineering
- languages
- rust
- networking
stage_binding: 3 rough
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- rust
- tcp
- reuseport
- accept
- scaling
- socket2
cross_links:
- rel: related_to
  target_object_id: PAT_drain_readiness_until_the_operation_would_block
reference:
  source_title: Network Programming with Rust
  author: Abhishek Chanda
confidence: medium
references: []
variants: []
---

# Scale Rust TCP Accept Across Cores with ReusePort Listeners

## Pattern Rule
**IF** measurement shows that one listening socket or accept path is the throughput bottleneck and the deployment platform provides suitable `SO_REUSEPORT` semantics
**THEN** consider one listener per worker, set port reuse before bind, and let the kernel distribute incoming connections across those listeners
**ELSE** prefer a shared listener or the runtime's normal accept distribution and optimize the actual per-connection bottleneck instead.

## Do
- Prove that admission is the bottleneck before adding listeners. Slow handlers, blocking work, and downstream saturation are not repaired by more accept queues.
- Create and configure the raw socket before bind and listen when a backlog or reuse option must differ from the standard library's defaults; a lower-level socket crate such as `socket2` exposes these controls.
- Gate the design by operating system and crate configuration. `set_reuse_port` is not uniformly available on every Rust target and its connection-distribution behavior is platform-defined.
- Keep accepted-stream ownership simple: each accepted connection should have one clear worker or runtime owner even when several listeners share the address.
- Compare the kernel-distribution design against a shared listener on the target workload; modern async runtimes may already distribute connection work effectively enough that extra listeners add complexity without throughput.

## Don't
- Do not equate `SO_REUSEPORT` with `SO_REUSEADDR`; both names and semantics vary by platform and neither is a portable synonym for the other.
- Do not assume one-listener-per-core is optimal merely because the machine has many cores.
- Do not combine several accept-distribution mechanisms without measuring where contention moved.
- Do not promise Windows support for a Unix-oriented reuse-port design without an explicit equivalent strategy.

## Checklist
- Is accept throughput or accept-lock contention actually visible in profiling or load tests?
- Does every deployment target support the required reuse-port behavior?
- Are reuse and backlog options set before bind and listen where required?
- Does the multi-listener version outperform a shared-listener runtime under realistic load?

## Notes
Port reuse is a specialized scaling tool, not a default server architecture. The attraction is moving connection distribution into the kernel before user-space workers contend on one accept path. Rust's standard listener intentionally hides much of the pre-bind socket configuration, so this design usually begins with a lower-level socket builder and therefore carries an explicit portability cost.
