---
object_id: PAT_make_rust_http_handler_contracts_visible_in_types
object_type: pattern
name: Make Rust HTTP Handler Contracts Visible in Types
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
foundation_object_id: PAT_convey_usage_through_names_and_types
tags:
- rust
- http
- handlers
- types
- api_design
cross_links:
- rel: related_to
  target_object_id: PAT_keep_rust_failures_as_result_until_recovery_context_exists
- rel: related_to
  target_object_id: PAT_choose_rust_http_stack_altitude
reference:
  source_title: Fullstack Rust
  author: Nate Murray
confidence: high
references: []
variants: []
---

# Make Rust HTTP Handler Contracts Visible in Types

## Pattern Rule
**IF** a Rust web framework can extract request data and convert response values through typed handler parameters and return types
**THEN** express each handler's required inputs and normal output or error contract in its signature
**ELSE** reach for a raw request or generic response only for behavior that cannot be represented cleanly by the framework's typed boundary.

## Do
- Accept the narrow extractor types that correspond to the data the handler actually consumes.
- Return a responder or result type that makes the success and failure shape visible at the function boundary.
- Let framework traits perform routine extraction and response conversion while keeping domain transformation in ordinary Rust types.
- Use a raw request only when the handler genuinely needs dynamic metadata or protocol details outside the typed extractor surface.
- Keep validation and error conversion explicit when extraction alone does not establish the domain invariant.

## Don't
- Don't accept a generic request object by default and hide every dependency in the function body.
- Don't return a generic response solely to avoid stating a useful output type.
- Don't mistake successful extraction for authorization, business validation, or persistence success.
- Don't let framework-specific wrapper types propagate into domain functions that do not need transport semantics.

## Checklist
- Can a reader identify required request data from the parameters alone?
- Does the return type expose the normal response and failure boundary?
- Is each raw-request dependency genuinely dynamic or protocol-specific?
- Are domain validation and authorization still performed at the appropriate layer?
- Can the core handler behavior be exercised with ordinary Rust values outside the transport adapter?

## Notes
Typed extraction and response conversion turn the Rust type checker into part of the HTTP boundary. The goal is not maximal type complexity; it is to make transport dependencies visible and narrow enough that the function signature remains a useful description of the handler.
