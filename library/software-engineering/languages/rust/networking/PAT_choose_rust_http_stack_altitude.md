---
object_id: PAT_choose_rust_http_stack_altitude
object_type: pattern
name: Choose Rust HTTP Components by Stack Altitude
library_path:
- software-engineering
- languages
- rust
- networking
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: PAT_specify_the_application_protocol_above_the_transport
tags:
- rust
- http
- hyper
- framework
- client
- networking
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

# Choose Rust HTTP Components by Stack Altitude

## Pattern Rule
**IF** a Rust program speaks HTTP
**THEN** choose the abstraction level from the lifecycle the program must own: use a low-level HTTP engine when connection and protocol plumbing are part of the design, a server framework when routing and application request handling are the problem, and a client library when the program only consumes HTTP services
**ELSE** do not hand-roll the HTTP wire protocol over raw TCP merely to avoid a dependency.

## Do
- Use the HTTP implementation layer rather than raw socket parsing for protocol framing, header grammar, body transfer, and version-specific state machines.
- Choose a low-level engine when the program must control connection upgrades, custom dispatch, protocol integration, or other behavior below a framework's request lifecycle.
- Choose a framework when the main work is routes, extractors or guards, application state, middleware, templating, and handler composition.
- Choose client and server libraries independently; consuming HTTP and hosting HTTP are different responsibilities even when they share protocol types underneath.
- Treat bodies as streams by default and make buffering the whole body an explicit size and latency decision.

## Don't
- Do not choose a low-level engine because it appears more "fundamental" when the application only needs ordinary routes and handlers.
- Do not choose a full framework when the program is embedding HTTP as one protocol inside a larger connection service and needs to own the lower lifecycle.
- Do not pin the architectural rule to one crate generation. The Rust HTTP ecosystem changes APIs faster than the engine/framework/client layering changes.
- Do not assume a convenient HTTP client is also the right server foundation, or vice versa.

## Checklist
- Does the program need to own connections, the request pipeline, or only handler logic?
- Are routing, extraction, middleware, and managed application state central requirements?
- Is the chosen client surface independent from the server choice?
- Is body buffering versus streaming deliberate?

## Notes
Current Rust HTTP documentation still describes `hyper` as a relatively low-level building block and points users who want higher-level server ergonomics toward frameworks and users who want a convenient client toward a client library. The durable coding decision is the altitude, not the current crate names.
