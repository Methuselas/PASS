---
object_id: PAT_explore_an_objects_api_with_dir_doc_and_help
object_type: pattern
name: Explore an Object's API with dir(), __doc__, and help()
library_path:
- software-engineering
- languages
- python
- documentation
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- documentation
- dir
- help
cross_links: []
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Explore an Object's API with dir(), __doc__, and help()

## Pattern Rule
**IF** encountering an unfamiliar object, module, type, or function and needing to learn what it offers or how to use it
**THEN** start with `dir(obj)` for the list of available attributes, `print(obj.__doc__)` for whatever written documentation is attached, and `help(obj)` for PyDoc's combined, formatted report of both plus structural details — before searching external documentation or reading source
**ELSE** when `help()`'s report is too terse for a genuinely complex library, move up to its full manual or project documentation; `help()` is a fast first stop, not a replacement for complete references

## Do
- Call `dir(obj)` first for a quick attribute inventory, and filter out interpreter-internal names with a comprehension — `[a for a in dir(obj) if not a.startswith('__')]` — when only the ordinary public API matters.
- Pass either a type name or an instance to `dir()` interchangeably; `dir(str)` and `dir('')` return the same list, since a type name like `str` is itself the type object.
- Reach for `help(obj)` as the default single command for learning an object's usage; it combines the object's docstring with automatically inspected structural information (call signatures, class hierarchy) into one readable report.
- Pass `help()` a function, method, type, module, or an actual instance — all work — and expect paging on longer reports at a plain interactive prompt (space for next page, Enter for next line, Q to quit).

## Don't
- Don't expect `dir()` to explain what an attribute means; it only lists names. Move to `__doc__` or `help()` for what a name actually does.
- Don't assume `help('somename')` (a bare string) always behaves like `help(somename)` (an actual reference); string arguments are treated specially, as a request for help on a possibly-unimported module by that name, and this handling has varied across Python versions.
- Don't skip straight to web search or source code for a builtin or standard-library object before trying `help()`; for most such objects it already has everything `dir()` and `__doc__` would have shown, assembled into one report.

## Checklist
- Has `dir()` been checked for what attributes exist before guessing or searching?
- Has `help()` been tried before reading source code or searching the web for a standard object's usage?
- When filtering `dir()`'s output, is the filter actually excluding only interpreter-internal names, not attributes that happen to start with an underscore for another reason?

## Notes
These three tools trade off completeness against ease of access: raw source is the most complete but least accessible; `dir()` is instant but gives only names; `__doc__` adds the author's own written explanation; `help()` adds automatically inspected structure on top of that. Reaching for them in roughly that order — attributes, then docstring, then the combined `help()` report — usually answers an API question faster than opening a browser.
