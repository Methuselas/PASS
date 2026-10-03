---
object_id: PAT_break_an_import_cycle_by_deferring_or_qualifying_the_import
object_type: pattern
name: Break an Import Cycle by Deferring or Qualifying the Import
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
- circular-import
cross_links:
- rel: related_to
  target_object_id: PAT_prefer_import_or_an_explicit_from_list_over_from_star
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Break an Import Cycle by Deferring or Qualifying the Import

## Pattern Rule
**IF** two modules need to import from each other — directly, or through a longer chain that loops back — and this produces an `ImportError` or `AttributeError` on a name that doesn't exist yet
**THEN** first try to remove the cycle by moving the names both sides need into a third module neither side needs to import back from; where the cycle genuinely cannot be removed, replace the risky side's `from module import name` with `import module` plus attribute qualification (`module.name`), or move that `from` import inside the function that actually needs it
**ELSE** when there is no cycle — module A imports module B, and B does not import A directly or transitively — ordinary top-level `import`/`from` statements need none of this and should stay exactly that simple

## Do
- Recognize the symptom: `ImportError: cannot import name 'Y'` when two modules import each other, because the module still partway through loading hasn't yet reached the assignment the other module wants.
- Prefer `import module` over `from module import name` across a cycle: a plain `import` only needs the module to already be present in `sys.modules` — Python's loaded-modules cache, populated *before* a module's body finishes running, which is exactly what stops a cycle from looping forever — and it defers the actual `module.name` lookup until the name is used, by which point loading has usually finished.
- Move a `from` import that must stay a `from` import inside the function or method that uses it, so the lookup happens long after both modules' top-level code has finished running, not during the cycle itself.
- Treat a recurring cycle as a design signal before reaching for either workaround: moving the shared pieces to a lower module that both sides import, instead of importing across the cycle, usually removes the need for the workaround entirely.

## Don't
- Don't use `from module import name` at the top level of two modules that import each other — the name may not exist yet in the partially executed module when the cycle runs.
- Don't treat a cycle as fixed just because importing one particular entry point happens not to fail; the same cycle can still fail from a different entry point, because which half of the cycle finishes loading first depends on which module a program imports first.
- Don't add more cross-imports to work around a cycle; that is the direction that created the problem. Removing a dependency — by relocating shared code to a module neither side needs to import back from — is the fix that doesn't just relocate the breakage.

## Checklist
- Does a `from module import name` sit at the top level of two modules that import each other, directly or transitively?
- Could the cycle be removed by moving the shared names to a third module instead of importing across the cycle at all?
- Where a cycle must remain, has the risky `from` import been replaced with `import` plus qualification, or deferred into a function body?

## Notes
Python never gets stuck in an infinite loop on a circular import: when a module import begins, Python records it in `sys.modules` immediately, before running any of its statements, so a second import reached mid-cycle finds that (possibly still-incomplete) module object already there and returns it rather than re-running the file. The partial-namespace problem this pattern addresses is a consequence of that short-circuit, not a failure of it.
