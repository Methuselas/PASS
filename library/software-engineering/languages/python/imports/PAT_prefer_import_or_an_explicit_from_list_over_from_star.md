---
object_id: PAT_prefer_import_or_an_explicit_from_list_over_from_star
object_type: pattern
name: Prefer import or an Explicit from List Over from Star
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
- namespaces
- modules
cross_links:
- rel: related_to
  target_object_id: PAT_copy_a_shared_mutable_object_to_the_depth_the_change_reaches
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Prefer import or an Explicit from List Over from Star

## Pattern Rule
**IF** choosing how to pull a name out of another module
**THEN** default to `import module` and qualify (`module.name`) for anything shared or long-lived, reach for `from module import name1, name2` with an explicit list only when the repeated qualification is genuinely costly, and reserve `from module import *` for at most one import per file
**ELSE** where the same bare name is needed from two different modules in one scope, use `import` (or `from module import name as alias`) rather than two competing `from` imports, since only one of them would survive

## Do
- Use `import` by default for anything another file will read later; `module.name` always tells the reader which file a name came from, with no need to search for it.
- List names explicitly in a `from` import (`from module import a, b`) rather than importing everything, so a reader can see the complete set an unqualified name might resolve to without opening the source module.
- Treat `from module import *` as acceptable for at most one module per file, and only when that module is designed to be used this way (it curates its public names, e.g. with `__all__`); a second star-import in the same file destroys any way to tell where a name came from short of searching every source file.
- Reach for `import` (or `from module import name as alias`) when the same bare name is needed from two different modules in one scope; a second `from` import of the same name silently replaces the first, with no error.
- Remember a `from` import still runs the entire target module's code; it only changes how many names get copied into the importer's scope afterward, not what gets loaded or executed.

## Don't
- Don't assume a name copied with `from` stays linked to its origin. `from mod import x` binds a name in your scope to whatever `mod.x` currently is; reassigning `x` in `mod` later does not change your copy, exactly as rebinding any name never affects another name bound to the same prior value (see `PAT_copy_a_shared_mutable_object_to_the_depth_the_change_reaches`). Only `import mod` followed by `mod.x = ...` reaches through to the module's own namespace, in either direction.
- Don't let a `from` import silently overwrite a name you're already using; `from module import *` in particular can clobber anything in your scope that happens to collide, with no warning at all.
- Don't reach for `from module import *` merely to save typing in ordinary application code; the convenience is real, but it collapses the module's namespace into yours, which is the one thing modules exist to prevent.

## Checklist
- Will this name be read by code outside the current file? If so, favor `import` and qualification.
- Does this `from` import list its names explicitly, or does it use `*`?
- Is more than one `from module import *` present in this file?
- Does any code here need the same bare name from two different modules in one scope?
- Does anything rely on a `from`-imported name tracking a later reassignment of that name in its source module?

## Notes
Both statements run the identical import operation underneath — locate the file, compile it if needed, execute its top-level code — and differ only in the bookkeeping step afterward: `import` binds one name to the module object, `from` binds additional names directly to whatever those attributes currently hold. That shared mechanism is also why a *mutable* object reached either way is the same shared object; what `from` loses is only the ability to see a later *name rebinding* in the source module, since a name, unlike an object, was never something more than one file could share.
