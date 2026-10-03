---
object_id: PAT_release_resources_with_a_context_manager_not_del
object_type: pattern
name: Release Resources with a Context Manager, Not __del__
library_path:
- software-engineering
- languages
- python
- classes
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- classes
- resources
- cleanup
cross_links:
- rel: related_to
  target_object_id: PAT_open_files_in_a_with_block_and_name_the_encoding
- rel: related_to
  target_object_id: PAT_give_every_acquired_resource_one_named_owner
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Release Resources with a Context Manager, Not __del__

## Pattern Rule
**IF** a class holds something that must be released — a file, socket, connection, lock, or subprocess
**THEN** give it an explicit `close()` and the `__enter__`/`__exit__` pair so callers release it deterministically with a `with` block, rather than relying on `__del__` to clean up when the object is collected
**ELSE** when the class holds only plain Python objects, write no cleanup at all; memory is reclaimed automatically and a destructor would add a hazard for no benefit

## Do
- Implement `__enter__` to return the usable object and `__exit__` to release it, so a `with` block guarantees cleanup on both normal exit and exception.
- Provide `close()` as well, for callers whose lifetime does not fit a single block, and make it safe to call twice.
- Reach for `contextlib.contextmanager` on a generator function when the setup and teardown are simple enough that a whole class is overkill.
- Use `__del__`, if at all, only as a last-resort safety net that warns about a leak — never as the mechanism the design depends on.
- Register cleanup with `contextlib.ExitStack` when the number of resources is not known until runtime.

## Don't
- Don't depend on `__del__` running at a predictable time. It fires when the last reference goes away, which a lingering reference in a cache, a traceback, or an exception object can postpone indefinitely — and it may not run at all for objects still alive at interpreter exit.
- Don't raise from `__del__`. Exceptions there cannot propagate to any sensible place, so they are reported to standard error and then discarded, leaving a failed cleanup that nothing can catch.
- Don't put cleanup only in `__del__` for a resource with a limited supply; file handles, sockets and connections run out long before memory pressure would force collection.
- Don't assume the garbage collector will reclaim objects in reference cycles promptly just because the cycle is unreachable; collection is deferred, and the release you wanted is deferred with it.

## Checklist
- Does every class holding an external resource support `with`, or at least an explicit `close()`?
- Is there any cleanup that happens *only* in `__del__`?
- Does `__exit__` release the resource even when the block exits by exception?
- Is `close()` safe to call more than once?

## Notes
The underlying problem is that object lifetime and resource lifetime are different things. Reference counting makes them coincide often enough to be misleading — the destructor usually does fire promptly — but "usually" is not a guarantee a limited resource can be managed on. A `with` block ties release to a point in the code rather than to a point in the object graph, which is both earlier and knowable by reading.
