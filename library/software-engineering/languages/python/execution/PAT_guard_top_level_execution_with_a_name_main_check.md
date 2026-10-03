---
object_id: PAT_guard_top_level_execution_with_a_name_main_check
object_type: pattern
name: Guard Top-Level Execution with a __name__ == "__main__" Check
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
- scripts
- testing
cross_links: []
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Guard Top-Level Execution with a __name__ == "__main__" Check

## Pattern Rule
**IF** a Python file may be both imported as a module and run directly as a program, or defines code — self-tests, a CLI entry point, a demonstration call — that must run only when the file itself is executed
**THEN** wrap that code in `if __name__ == "__main__":` at module level, since Python sets the module's built-in `__name__` to the string `"__main__"` only when this file is the one started directly, and to the module's own name (as known to importers) whenever it is imported instead
**ELSE** for a file that is purely an importable library with no standalone behavior, skip the check entirely — guarding code that never runs standalone just adds a branch nobody exercises

## Do
- Use the guard for self-test code, so running the file directly exercises it, but importing the module as a library elsewhere does not trigger the tests as a side effect.
- Use the guard for a command-line entry point (reading `sys.argv`, calling a `main()` function) so the same file works both as `python tool.py ...` and as `import tool; tool.main(...)`.
- Place the guard after every `def` it depends on, at the bottom of the file — the names it calls must already exist by the time the guarded block runs.
- Expect the same mechanism to work unchanged for a package submodule run with `python -m package.module`; `__name__` is still set to `"__main__"` for the module actually launched.
- Remember `__name__` needs no import and no special setup — Python creates and assigns it automatically as the first thing it does when loading any file.

## Don't
- Don't put an observable side effect (printing, mutating shared state, opening a resource) at module top level, outside the guard, in a file that is also meant to be imported — every importer pays for it on every import.
- Don't invent a different convention for this ("if running standalone", a custom flag) — `__name__ == "__main__"` is the idiom nearly every Python file in the wild uses for exactly this test, so deviating costs a reader more than it saves.
- Don't treat `__name__` as meaningful for anything beyond this usage-mode test and basic introspection (e.g., in error messages); it carries no other special behavior.
- Don't forget that typing code at the interactive prompt, or running `python -c "..."`, also executes with `__name__ == "__main__"` — the check is "am I the thing that was launched," not "am I a saved file."

## Checklist
- Is every piece of code meant to run only when this file is executed placed inside `if __name__ == "__main__":`?
- Does anything at module top level, outside the guard, have an observable effect when the file is merely imported?
- Does the guard sit after all the `def`s (and any class statements) it calls, near the bottom of the file?

## Notes
The check is a usage-mode flag, not a language feature with its own syntax: `__name__` is an ordinary module attribute, and the `if` is an ordinary `if`. What makes it work is purely that Python decides the attribute's value — `"__main__"` or the module's import name — before a single line of the file's own code runs, so the test is reliable no matter where in the file it appears, as long as it appears after whatever it calls.
