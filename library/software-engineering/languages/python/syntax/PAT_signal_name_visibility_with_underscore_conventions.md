---
object_id: PAT_signal_name_visibility_with_underscore_conventions
object_type: pattern
name: Signal Name Visibility with Underscore Conventions
library_path:
- software-engineering
- languages
- python
- syntax
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- syntax
- naming
- visibility
cross_links: []
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Signal Name Visibility with Underscore Conventions

## Pattern Rule
**IF** choosing how to name a variable, function, or attribute that is internal, special, or otherwise not meant for ordinary public use
**THEN** match the underscore convention to the intent — one leading underscore (`_x`) for "internal, don't import this with `*`," double leading-and-trailing underscores (`__x__`) reserved for names the interpreter itself defines, double-leading-only (`__x`) when per-class name mangling is specifically wanted — rather than inventing an ad hoc scheme or leaving the name looking like any other public one
**ELSE** for an ordinary name meant to be used freely by callers, skip every underscore convention and use a plain identifier

## Do
- Prefix an internal name with one underscore (`_helper`) when a module's names may be imported with `from module import *`; that convention is actually enforced — a single-leading-underscore name is skipped by the star import, every other name is not.
- Reserve the double-leading-and-trailing pattern (`__init__`, `__name__`) for names Python itself defines and recognizes; inventing a dunder name of your own does not grant special interpreter behavior, it only invites confusion with ones that do.
- Remember that a double-leading-underscore name (`__x`) inside a class body is not hidden, it is renamed (mangled) to include the enclosing class's name — a narrower and different guarantee than "private."
- Treat the single standalone underscore (`_`) as the interactive interpreter's "last expression result" name; avoid binding it to anything meant to be kept in a script, where no such automatic behavior exists.

## Don't
- Don't expect a single leading underscore to block access the way a language with real private members would; it is a convention observed by `from module import *` and nothing else enforces it.
- Don't pick the double-leading-and-trailing pattern for ordinary names "to look special"; it collides with the namespace Python reserves for itself.
- Don't name a variable, parameter, or attribute after a built-in you still need in that scope — `list`, `dict`, `id`, `type`, `input`, `open`: the assignment is legal and unwarned, and the built-in simply becomes unreachable by that name for the rest of the scope. At an interactive prompt, `del name` removes the shadow and restores the original.
- Don't be surprised when a double-leading-underscore attribute can't be found by its plain name from outside its class — look for the mangled name instead of assuming it was never set.

## Checklist
- Does an internal helper meant to be excluded from `import *` actually start with a single underscore?
- Does any name using the double-leading-and-trailing pattern belong to Python itself, not to application code?
- Is a double-leading-underscore name being used because per-class mangling is actually wanted, not by habit?

## Notes
These are enforced behaviors, not mere style advice — the single-underscore exemption from `import *` and the double-leading-underscore mangling are both carried out by the interpreter itself, which is what separates them from a capitalization or spacing convention that Python does not check at all.
