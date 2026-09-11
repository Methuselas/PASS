---
object_id: PAT_never_let_exceptions_leave_a_destructor
object_type: pattern
name: Never Let Exceptions Escape a Destructor
library_path:
- software-engineering
- languages
- cpp
- destructors
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- destructors
- exceptions
- resource_management
cross_links:
- rel: related_to
  target_object_id: PAT_dont_hide_errors
reference:
  source_title: 'Effective C++, Third Edition: 55 Specific Ways to Improve Your Programs and Designs'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Never Let Exceptions Escape a Destructor

## Pattern Rule
**IF** a destructor performs an operation that might throw — closing a connection, flushing a buffer
**THEN** prevent failure from escaping the destructor, apply a documented containment policy, and give clients a normal operation that can report the failure before destruction becomes the fallback.

## Do
- Keep the destructor non-throwing and catch any failure from cleanup it must attempt. Record it through a genuinely non-throwing diagnostic path, swallow it only when the class contract permits that loss, or deliberately terminate when continuing would violate invariants.
- Provide a normal function such as `close()` or `commit()` that performs the fallible operation and reports errors, keeping only best-effort cleanup in the destructor for clients that did not invoke it.
- Remember that destructors are normally non-throwing by default. An exception escaping a non-throwing destructor calls `std::terminate`, whether or not stack unwinding was already in progress.

## Don't
- Don't mark a destructor `noexcept(false)` merely to permit failure propagation. If it is invoked while another exception is unwinding and throws, the program terminates; containers and generic code also commonly rely on destruction being non-throwing.
- Don't perform the first and only observable attempt at required I/O or transaction commit in a destructor. Destruction has no ordinary return channel through which the caller can respond.

## Checklist
- Can anything this destructor calls throw, and if so is it caught so nothing escapes?
- Is there a non-destructor function clients can call to handle the failure themselves?

## Notes
If a destructor throws while another exception is already unwinding, C++ calls `std::terminate`; a normally non-throwing destructor also terminates on any escaping exception. That is defined failure behavior, not undefined behavior, and it is why destruction must contain fallible cleanup. Containment still discards the client's ordinary chance to react, so the better design exposes a normal `close()`-style operation and keeps destruction as a non-throwing fallback.
