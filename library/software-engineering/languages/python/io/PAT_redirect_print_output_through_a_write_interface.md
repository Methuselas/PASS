---
object_id: PAT_redirect_print_output_through_a_write_interface
object_type: pattern
name: Redirect Print Output Through a Write Interface
library_path:
- software-engineering
- languages
- python
- io
stage_binding: 3 rough
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- print
- io
- duck-typing
cross_links: []
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Redirect Print Output Through a Write Interface

## Pattern Rule
**IF** every `print()` call in a program, not just one call, needs to go somewhere other than the console — a log file, a GUI widget, a test capture
**THEN** reassign `sys.stdout` to any object that has a `write(text)` method, saving the original stream first, and restore it when done; every `print` anywhere in the process keeps calling the same `write` method it always did, now pointed somewhere else
**ELSE** when only one or a few specific calls need redirecting, leave `sys.stdout` alone and pass `file=destination` on just those calls instead

## Do
- Save the current `sys.stdout` to a variable before reassigning it, so the original stream can be restored later — nothing does this automatically.
- Hand `sys.stdout` any object exposing a `write(text)` method, not only a real file; a small class with its own `write` method can route, colorize, or duplicate the text however it needs to.
- Restore the saved stream explicitly once redirected output is no longer needed, rather than leaving the program's output silently pointed at the redirected target.
- Prefer per-call `file=` redirection over reassigning `sys.stdout` whenever only specific calls, not the whole program, need to go elsewhere.

## Don't
- Don't reassign `sys.stdout` for a single print call; that is a global, program-wide change for a local need — pass `file=` to that one call instead.
- Don't forget to close or flush a file-backed redirect target before relying on its contents; buffered output may not be on disk yet when reading it back.
- Don't assume the replacement object must be a `file`; anything with a matching `write(text)` method works, because `print` only ever calls that one method on whatever `file` (or `sys.stdout`) currently refers to.

## Checklist
- Was the original `sys.stdout` saved before being reassigned?
- Is the replacement object's `write` method compatible with the text `print` sends it?
- Is `sys.stdout` restored once the redirected section of the program is done?
- Would per-call `file=` have been simpler for what was actually being redirected?

## Notes
This works because `print` never checks what kind of object `file` (or `sys.stdout`) is — it only calls `.write(text)` on it, the same contract every open file satisfies. That makes redirection a special case of a more general technique: substituting any object that honors an expected interface for the one a piece of code was originally written against, with no change to the calling code required.
