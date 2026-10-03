---
object_id: PAT_put_function_defs_before_top_level_code_that_calls_them
object_type: pattern
name: Put Function Defs Before Top-Level Code That Calls Them
library_path:
- software-engineering
- languages
- python
- execution
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- execution
- modules
- ordering
cross_links:
- rel: related_to
  target_object_id: PAT_resolve_names_by_legb_and_let_assignment_decide_scope
- rel: related_to
  target_object_id: PAT_guard_top_level_execution_with_a_name_main_check
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Put Function Defs Before Top-Level Code That Calls Them

## Pattern Rule
**IF** a module mixes `def` statements with top-level code — statements outside any function body — that calls those functions
**THEN** place every `def` the top-level code depends on before the call that uses it, and keep ordinary driver code (including any `__main__` guard) at the bottom of the file, since Python executes a module's statements strictly top to bottom and a name does not exist until the statement that assigns it — including a `def` — has actually run
**ELSE** a call made from *inside* another function's body needs none of this ordering: a function body isn't executed until the function is called, so names it references are looked up at call time, by which point the rest of the module has typically already finished loading

## Do
- Group `def` and `class` statements near the top of a module, with any unconditional top-level calls, self-tests, or script-driver logic at the bottom.
- Let a function's body reference a `def` that appears later in the same file, as long as that later `def` has run by the time the function is actually called — forward references are fine inside function bodies.
- Read a `NameError` raised while a module is merely being imported (not while a specific function is being called) as exactly this problem: some statement ran before the name it needed was defined.
- Keep this rule in mind for the `__main__` guard specifically: place it after the `def`s it calls, at the very bottom of the file (see `PAT_guard_top_level_execution_with_a_name_main_check`).

## Don't
- Don't scatter top-level calls between `def`s, expecting a later `def` to "already be there" — only the statements before a given point in the file have executed by the time that point is reached.
- Don't confuse this with scope resolution; this is purely about execution order within one top-to-bottom pass through the file, independent of how LEGB would eventually resolve a name once everything has run (see `PAT_resolve_names_by_legb_and_let_assignment_decide_scope`).
- Don't assume a `class` body is exempt from this — a class body executes immediately, exactly like plain module-level code, so a class body that references a not-yet-defined function at class-definition time hits the identical hazard.

## Checklist
- Does every top-level statement in this file reference only names already assigned earlier in the same file?
- Are the `def`s a module needs grouped before the driver code — including any `__main__` guard — that calls them?
- When a `NameError` appears at import time rather than inside a function call, has statement order been checked before scope?

## Notes
This follows directly from how a module executes: the first import of a file runs its statements once, in file order, and `def` is itself just a runtime statement that assigns a function object to a name — it has no special hoisting the way some other languages' declarations do. The same top-to-bottom execution model is what a reload re-runs (see `PAT_rerun_edited_python_code_in_a_fresh_process`), so this ordering requirement applies identically to a reloaded module.
