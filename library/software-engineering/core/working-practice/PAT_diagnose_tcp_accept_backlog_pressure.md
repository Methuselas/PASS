---
object_id: PAT_diagnose_tcp_accept_backlog_pressure
object_type: pattern
name: Diagnose TCP Failures under Accept Backlog Pressure
library_path:
- software-engineering
- core
- working-practice
stage_binding: 4 final
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- tcp
- networking
- backlog
- accept
- overload
- diagnosis
cross_links:
- rel: related_to
  target_object_id: PAT_drain_readiness_until_the_operation_would_block
reference:
  source_title: Network Programming with Rust
  author: Abhishek Chanda
confidence: high
references: []
variants: []
---

# Diagnose TCP Failures under Accept Backlog Pressure

## Pattern Rule
**IF** connection attempts begin timing out, resetting, or being refused during bursts even though the server process and listening port remain present
**THEN** test whether the accept path is draining the listener fast enough and whether its configured or platform-capped backlog is overflowing before diagnosing the symptom as a dead service
**ELSE** investigate ordinary routing, firewall, bind, and process-liveness causes first.

## Do
- Reproduce under controlled load while deliberately slowing or pausing accept to see whether the client symptom tracks queue pressure.
- Keep heavy initialization, name resolution, parsing, authentication, and request work out of the accept loop; accept promptly and transfer established connections to their processing path.
- Inspect both the requested listen backlog and the operating system's effective cap. The kernel may clamp the value or apply additional queue limits.
- Treat overflow behavior as platform policy. Some systems drop or defer connection progress; Linux can reset on overflow when `tcp_abort_on_overflow` is enabled, while its default policy tries to recover instead.
- Increase backlog only after proving that burst absorption, rather than sustained processing capacity, is the problem.

## Don't
- Do not read one `ECONNREFUSED` or timeout symptom as proof that no process is listening.
- Do not treat the accept backlog as an application request queue; it holds connections waiting to be accepted.
- Do not hide an accept path that is permanently slower than arrivals by making the queue arbitrarily deeper.
- Do not assume backlog values or overflow symptoms are portable between operating systems.

## Checklist
- Does the failure appear only under connection bursts or a deliberately stalled accept loop?
- How quickly does the program return to `accept` after each connection?
- What backlog did the program request, and what effective cap does the deployment kernel apply?
- Does tuning the backlog absorb short bursts without changing the sustained overload point?

## Notes
A listening TCP socket is a bounded admission point. When the application stops draining it fast enough, client-visible failures depend on the operating system and its queue policy, so the same server bug may look like a timeout, retry storm, reset, or refusal on different systems. Diagnose the queue and accept rate rather than overfitting to one errno.
