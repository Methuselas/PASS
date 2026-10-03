---
object_id: PAT_fetch_an_attribute_dynamically_with_getattr
object_type: pattern
name: Fetch an Attribute Dynamically with getattr
library_path:
- software-engineering
- languages
- python
- objects
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- objects
- introspection
- dynamic-dispatch
cross_links:
- rel: related_to
  target_object_id: PAT_code_to_what_an_object_can_do_not_its_type
- rel: related_to
  target_object_id: PAT_dispatch_a_multiway_branch_with_a_dict_instead_of_an_elif_chain
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Fetch an Attribute Dynamically with getattr

## Pattern Rule
**IF** the attribute, method, or module-level name to access is known only at runtime as a string — from user input, a config value, a dispatch table, or iteration over a namespace — rather than hardcoded in the source
**THEN** fetch it with `getattr(obj, name_string)`, or `getattr(obj, name_string, default)` to tolerate a missing name without an exception, instead of trying to build literal attribute-access syntax out of the string
**ELSE** when the attribute's name is known while writing the code, use plain attribute access (`obj.name`) — it is faster, checkable by tools, and greppable; reserve `getattr` for the genuinely dynamic case

## Do
- Reach for `getattr(obj, name, default)` to look up optional hooks or configuration-driven behavior without a `try`/`except AttributeError`.
- Know the equivalences for a module `M`: `M.name`, `M.__dict__['name']`, and `getattr(M, 'name')` all reach the same attribute and object; `getattr` is the one of these that takes the name as an ordinary runtime expression.
- Use `setattr(obj, name_string, value)` as `getattr`'s write counterpart when an attribute must be assigned by a name computed at runtime.
- Pair `getattr` with its default argument, or with `hasattr(obj, name)`, to probe for an optional capability by presence rather than checking the object's type first.
- Iterate `sorted(obj.__dict__)` or `dir(obj)` to enumerate available names, then `getattr` each one, when building a generic listing, introspection, or serialization tool.

## Don't
- Don't build attribute access by string concatenation and `eval`/`exec` (e.g. `eval("obj." + name)`); that is slower, an injection hazard if the name string is not fully trusted, and `getattr` is the direct tool for exactly this job.
- Don't call `getattr(obj, 'literal_name')` where the name is actually a fixed literal known while writing the code — that is only a slower, less readable `obj.literal_name`.
- Don't assume `getattr` without a default behaves differently from dot access on failure; it raises the same `AttributeError` — pass a default or catch the error, don't assume the name is guaranteed to exist.

## Checklist
- Is the attribute name genuinely a runtime value (a string variable or expression), not a literal that could be written directly?
- Does the `getattr`/`hasattr` call carry a default, or is a missing attribute truly meant to be fatal here?
- Would a dict-based dispatch table make the intent clearer to a reader than a `getattr` call built around a computed name?

## Notes
`getattr`, `setattr`, and `hasattr` are the runtime-string-named counterparts of ordinary attribute syntax, and they are what lets a module's own machinery — `help()`, `dir()`, serializers, plugin loaders, object-relational mappers — process arbitrary objects generically instead of being written against one fixed set of names.
