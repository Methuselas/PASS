---
object_id: PAT_write_docstrings_for_functional_documentation_reserve_hash_comments_for_local_notes
object_type: pattern
name: Write Docstrings for Functional Documentation, Reserve Hash Comments for Local Notes
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
- docstrings
cross_links: []
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Write Docstrings for Functional Documentation, Reserve Hash Comments for Local Notes

## Pattern Rule
**IF** documenting Python code — a module, function, class, or a single tricky expression or statement
**THEN** write a docstring (a string literal as the first statement in the module, function, or class) for functional documentation of what the whole unit does and how to use it, and reserve `#` comments for small-scale notes about why one specific, non-obvious expression or statement does what it does
**ELSE** when there's nothing non-obvious to explain, skip the comment; neither form is owed to code that already reads clearly

## Do
- Put a docstring as the very first statement of a module, function, or class — before any other code, though after a shebang line or encoding declaration if present — so Python attaches it to the object's `__doc__` attribute automatically.
- Use a triple-quoted string for any docstring that spans more than one line, and a plain quoted string for a true one-liner; both are retained the same way.
- Write docstrings at the "what does this do and how do I use it" level — a module's purpose, a function's contract, a class's role — and reserve `#` comments for the "why does this strange line do that" level, next to the line in question.
- Print a docstring (`print(obj.__doc__)`) rather than just evaluating it at the interactive prompt, so multiline text displays as intended instead of as one string with literal `\n` sequences.

## Don't
- Don't put your only documentation in `#` comments for anything meant to explain a whole module, function, or class; comments are visible only to someone reading the source, while a docstring is retained at runtime and surfaced by tools like `help()`.
- Don't invent your own markup scheme (HTML, XML, or similar) inside docstrings expecting tooling support for it; there is no broadly adopted standard for docstring structure, and plain, clear prose is common practice.
- Don't let a class's or function's docstring go stale as the code around it changes; an inaccurate docstring is worse than none, because `help()` and `__doc__` present it as authoritative.

## Checklist
- Does every module, function, and class meant to be used by others start with a docstring?
- Do `#` comments cluster around specific non-obvious lines rather than standing in for missing functional documentation?
- Would `print(obj.__doc__)` display the intended text correctly, including its line breaks?

## Notes
This split exists because the two forms are retained differently: a docstring survives into the running object as `__doc__` and is what tools like `help()` and PyDoc read, while a `#` comment exists only in the source text a human happens to be looking at. Writing the functional summary as a comment instead of a docstring doesn't just misplace it stylistically — it makes that documentation invisible to every tool built to surface it.
