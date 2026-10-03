---
object_id: PAT_declare_the_public_api_with_all
object_type: pattern
name: Declare a Module's Public API with __all__
library_path:
- software-engineering
- languages
- python
- imports
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- imports
- modules
- api
- namespaces
cross_links:
- rel: related_to
  target_object_id: PAT_signal_name_visibility_with_underscore_conventions
- rel: related_to
  target_object_id: PAT_prefer_import_or_an_explicit_from_list_over_from_star
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Declare a Module's Public API with __all__

## Pattern Rule
**IF** a module should export a specific, curated subset of its top-level names as its intended public interface, and that boundary should be both documented and enforced against `from module import *`
**THEN** assign a list of those names' strings to `__all__` at module level; Python copies out exactly the names listed there — and only those — whenever a client does `from module import *`
**ELSE** for a module with no star-import boundary to curate, skip `__all__` and either rely on the default (every top-level name without a leading underscore is copied by `from *`) or mark individual internal names with a single leading underscore instead

## Do
- Treat `__all__` as living documentation of the module's public surface: a reader (or a tool) can see the intended interface in one list, without scanning every assignment for a leading underscore.
- Know that `__all__` takes precedence over the underscore convention completely: if `__all__` is present, `from *` copies exactly its names — even ones that start with an underscore — and the single-leading-underscore exclusion rule is not consulted at all.
- Use `__all__` in a package's `__init__.py` to declare which submodules or names a `from package import *` re-exports, on top of whatever it does for an ordinary module.
- Keep `__all__` in sync with what the module actually defines by construction (e.g., build it alongside the definitions, or generate it), since nothing else checks the two lists for consistency.

## Don't
- Don't expect `__all__` to restrict plain `import module` or an explicit `from module import specific_name` — both still reach any name that exists in the module's namespace; `__all__` governs only the `*` wildcard form.
- Don't list a name in `__all__` that the module doesn't actually define at import time — a client's `from module import *` raises `AttributeError` the moment it tries to copy that missing name.
- Don't expect `__all__` to hide anything from `dir(module)`, `help(module)`, or `module.__dict__` — all of those still show every name; only the star-import copy is filtered.

## Checklist
- Does every name listed in `__all__` actually exist in the module by the time `from module import *` would run?
- If the module also uses single-leading-underscore names, is it clear that `__all__`'s presence makes that convention irrelevant for this module's star-imports?
- Is `__all__` being relied on only for the star-import boundary, not assumed to provide privacy or hide names from introspection?

## Notes
`__all__` is the converse of the `_name` convention: `_name` is an exclusion list applied name by name (skip this one), while `__all__` is an inclusion list applied to the whole module (copy only these). Python looks for `__all__` first; only its absence makes the per-name underscore convention take effect for `from *`.
