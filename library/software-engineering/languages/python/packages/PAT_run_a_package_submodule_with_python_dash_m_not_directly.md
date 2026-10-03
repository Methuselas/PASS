---
object_id: PAT_run_a_package_submodule_with_python_dash_m_not_directly
object_type: pattern
name: Run a Package Submodule with python -m, Not Directly
library_path:
- software-engineering
- languages
- python
- packages
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- packages
- imports
- relative-imports
- entry-points
cross_links:
- rel: related_to
  target_object_id: PAT_use_a_dotted_from_import_for_sibling_modules_in_a_package
- rel: related_to
  target_object_id: PAT_rerun_edited_python_code_in_a_fresh_process
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Run a Package Submodule with python -m, Not Directly

## Pattern Rule
**IF** a file inside a package uses a relative import (`from . import sibling`) and also needs to be launched directly rather than only imported
**THEN** launch it with `python -m package.module` (or `python -m package.sub.module`) so Python sets up the package context the relative import needs, instead of running the file's own path
**ELSE** where the file genuinely never needs to run on its own — it's imported only — leave it as an ordinary package submodule with no launch concerns at all

## Do
- Launch a package submodule by its dotted module path — `python -m mypkg.sub.spam` — whenever that file contains a relative import; `-m` executes the module as part of its package, which gives relative imports the parent-package context they require.
- Keep a file's role consistent: either it's a package submodule reached through dotted imports, or it's a standalone script using ordinary absolute imports — not both, unless it's launched with `-m` every time.
- Put true command-line entry points in a thin top-level script (or a console-script entry point in packaging metadata) that imports from the package with an absolute path, rather than inside a file that also uses relative imports.
- Use an absolute, fully qualified import (`import mypkg.sibling`) instead of a relative one in any file that must keep working when run directly as a plain script (`python mypkg/sibling.py`); absolute imports don't depend on package context and work either way, as long as the package's root is importable.
- Reproduce the failure once on purpose — run a relative-import file directly and read the `ImportError: attempted relative import with no known parent package` message — so the fix (`-m`, or switching to absolute imports) is recognized immediately the next time it appears.

## Don't
- Don't run `python path/to/pkg/sub/spam.py` on a file containing `from . import sibling` and expect it to work; running a file directly never gives it a package identity, so Python has no package to resolve the dots against, regardless of the file's location on disk.
- Don't add `sys.path` hacks or try/except import fallbacks to a module purely to make both direct execution and relative imports work in the same file; it papers over a structural choice that absolute imports or `-m` already solve directly.
- Don't scatter self-test code behind relative imports inside deeply nested package files; either run those tests through `-m`, or keep test entry points in files that use absolute imports so they can run either way.
- Don't assume moving the file to a shallower or deeper directory fixes the problem; the failure is about how the file is launched (as a script vs. as a module), not about its position in the tree.

## Checklist
- Does this file use any relative (`from .`) import, and is it also ever launched directly?
- Is it launched with `python -m package.module`, or with a bare file path?
- Would switching this file's imports to an absolute, fully qualified form remove the need for `-m` entirely?
- Are command-line entry points isolated in files that don't themselves use relative imports?

## Notes
Direct execution (`python file.py`) runs the file with `__name__` set to `"__main__"` and no parent package at all — there's nothing for a leading dot to mean. The `-m` flag instead locates the named module through the normal import system and executes it as that module, which is what supplies the package context a relative import needs. This is a different problem from re-running edited code — see `PAT_rerun_edited_python_code_in_a_fresh_process` for that — but the two often collide in practice, since a quick `python somefile.py` to check an edit is exactly the moment this failure shows up.
