---
object_id: PAT_import_a_module_by_name_string_with_importlib
object_type: pattern
name: Import a Module by Name String with importlib
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
- dynamic-loading
- plugins
cross_links:
- rel: related_to
  target_object_id: PAT_fetch_an_attribute_dynamically_with_getattr
- rel: related_to
  target_object_id: PAT_parse_untrusted_text_instead_of_evaluating_it
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Import a Module by Name String with importlib

## Pattern Rule
**IF** the module to import is known only as a string computed at runtime — a plugin name, a config value, a CLI argument — rather than a literal name an `import` statement can reference
**THEN** load it with `importlib.import_module(name)`, which returns the module object directly, and capture that return value in a variable
**ELSE** when the module's name is a literal known while writing the code, use a normal `import`/`from` statement — it is checked earlier, read by tooling, and needs none of this machinery

## Do
- Use `importlib.import_module("pkg.mod")` for plugin- or driver-style loading, where the set of available choices comes from configuration or from scanning a directory rather than from fixed `import` statements.
- Assign its return value to a name yourself; unlike a literal `import` statement, nothing is bound automatically into any namespace.
- Pass the optional `package=` argument when resolving a relative module name against a package context.
- Combine a dynamically imported module with `getattr` to fetch the specific class, function, or constant the caller expects it to provide (see `PAT_fetch_an_attribute_dynamically_with_getattr`).
- Treat `importlib.import_module` as the current preferred spelling for this job; it is what the standard library's own documentation points to for importing by name string.

## Don't
- Don't use `exec("import " + modname)` to do this: it compiles and runs an entire statement of code on every call, costs more than a direct call, and is an injection hazard if the name string is ever built from untrusted input (see `PAT_parse_untrusted_text_instead_of_evaluating_it`).
- Don't reach for the lower-level `__import__` built-in directly in new code; it exists mainly so the import mechanism itself can be customized, not for ordinary dynamic loading, and for a dotted name its return value is the top-level package rather than the named submodule — a routine source of confusion.
- Don't assign a literal module name to a variable and pass it to an `import` statement expecting the string's value to be imported; `import` takes a hardcoded name token, not an expression — `import x` where `x` happens to hold the string `'string'` tries to import a file literally named `x.py`.

## Checklist
- Is the module's name genuinely unavailable until runtime, not merely inconvenient to spell out as a literal?
- Is `importlib.import_module` used here, rather than `exec` or the bare `__import__` built-in?
- Is the returned module object captured and used directly, instead of assuming a name will appear automatically in the caller's own namespace?

## Notes
`__import__` predates `importlib` and still works, but it was always intended as the low-level hook the import statement itself calls, which current Python's own documentation no longer recommends for direct use; `importlib.import_module` wraps it with behavior that matches what an ordinary `import` statement does — including running the target package's `__init__` chain — more predictably for this exact job.
