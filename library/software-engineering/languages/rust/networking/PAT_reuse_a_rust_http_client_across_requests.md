---
object_id: PAT_reuse_a_rust_http_client_across_requests
object_type: pattern
name: Reuse a Rust HTTP Client Across Requests
library_path:
- software-engineering
- languages
- rust
- networking
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- rust
- http
- client
- connection_pooling
- reqwest
- performance
cross_links:
- rel: related_to
  target_object_id: PAT_choose_rust_http_stack_altitude
- rel: related_to
  target_object_id: PAT_reuse_database_connections_through_a_pool
reference:
  source_title: Fullstack Rust
  author: Nate Murray
confidence: high
references: []
variants: []
---

# Reuse a Rust HTTP Client Across Requests

## Pattern Rule
**IF** a Rust process may issue multiple HTTP requests with the same client policy or destination ecosystem
**THEN** construct one configured HTTP client for the appropriate lifetime and reuse that client across requests so its connection pool and transport configuration can be reused
**ELSE** for a genuinely one-shot process that will issue only one request, a request-local client can be acceptable when the lost reuse and repeated setup are immaterial

## Do
- Construct the client near the application or service composition boundary, configure TLS, proxy, timeout, redirect, and pool policy once, and pass the client to request logic.
- Reuse the same client handle for related requests so idle connections and transport setup can be reused when the protocol and peer permit it.
- Choose the asynchronous or blocking client surface to match the execution model; isolate blocking HTTP work from asynchronous executor threads.
- Treat client reuse as permission to reuse connections, not a guarantee that every request will use the same socket.
- Test client-level policy such as timeouts, proxy behavior, redirects, and authentication defaults at the boundary where the reusable client is built.

## Don't
- Do not call Client::new inside an ordinary per-request function when the process will make repeated HTTP requests.
- Do not rebuild identical client configuration for each request just because request builders themselves are short-lived.
- Do not add an extra Rc or Arc solely to share an async reqwest Client; use the client type's documented cheap clone/share behavior.
- Do not assume pooling makes a blocking client safe to call directly from an async executor.

## Checklist
- Will this process or service make more than one HTTP request during the client lifetime?
- Is client configuration stable enough to construct once and reuse?
- Does request logic receive the reusable client instead of constructing its own?
- Is the chosen client API compatible with the surrounding blocking or async runtime?
- Are connection-pool and timeout settings deliberate for the expected request pattern?

## Notes
In current reqwest, Client owns an internal connection pool specifically to reuse connections and avoid setup overhead. Request builders remain per-request values; the reusable lifetime belongs to the client that owns transport policy and pooled connections.
