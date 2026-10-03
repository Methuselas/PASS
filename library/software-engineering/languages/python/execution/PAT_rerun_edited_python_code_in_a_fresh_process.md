---
object_id: PAT_rerun_edited_python_code_in_a_fresh_process
object_type: pattern
name: Rerun Edited Python Code in a Fresh Process
library_path:
- software-engineering
- languages
- python
- execution
stage_binding: 3 rough
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- execution
- imports
- reload
- repl
cross_links: []
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Rerun Edited Python Code in a Fresh Process

## Pattern Rule
**IF** you have edited a Python source file and need to see what the changed code now does
**THEN** run it again as a new interpreter process — `python file.py`, `python -m package.module`, or the editor's run command — rather than importing it again, reloading it, or `exec`-ing its text into a live session
**ELSE** when a long-lived interactive session is worth keeping, reload only the one module under test with `importlib.reload`, reach its names through the module object, and restart the session the moment results stop making sense.

## Do
- Treat a second `import m` in the same process as a no-op: the module object is cached in `sys.modules` after the first import, so edits saved since then are invisible until the process restarts or the module is reloaded.
- Reload with `importlib.reload(m)`; it re-executes the module's current source into the existing module object and returns it. The old `imp.reload` spelling no longer exists (the `imp` module was removed in Python 3.12).
- After a reload, refer to `m.name`, not to names you pulled out earlier with `from m import name` — those are copies bound in your own namespace and still point at the old objects.
- Reload every edited module yourself, in dependency order: `reload` re-executes only the module you pass, not the modules it imports.
- To run a file for its results without disturbing your session, use `runpy.run_path("file.py")`; it executes in a fresh namespace and returns that namespace as a dictionary.
- Confirm behaviour that an IDE supplied under plain `python` before relying on it: some IDE run commands change the working directory, add the file's folder to the import path, or leave the script's variables in the shell, and none of that happens when the program runs on its own.

## Don't
- Don't run a file with `exec(open("file.py").read())` inside a session or module you care about: the code runs in your current namespace and silently overwrites any variable with the same name (a script assigning `x` replaces your `x`).
- Don't trust a surprising result from a session that has seen several reloads; stale objects created before the reload (instances of the old class, callbacks, `from`-copied functions) keep running the old code alongside the new.
- Don't launch the compiled `.pyc` in place of the source while developing; Python does not check a byte-code file against source it was not given, so you run whatever was last compiled.

## Checklist
- Was the changed code exercised by a new process or an explicit reload, not by a repeated `import`?
- After a reload, are all uses going through `module.attribute` rather than earlier `from` copies?
- Were modules imported by the edited module reloaded too, or the process restarted?
- Does the behaviour still hold when run with plain `python`, outside the IDE?

## Notes
Python imports a module once per process: the first import finds the file, compiles it to byte code (cached under `__pycache__` for imported modules, never for the top-level script), and executes it; later imports hand back the cached module object. That is what makes imports cheap, and it is why "edit, then import again" is the most common way to test code that has not actually run.

Reloading is a tool for interactive exploration, not a development loop. It rebinds the module's names in place, but any reference that escaped before the reload — a `from` import, an instance of a class defined in the module, a function stored in a registry — still refers to the old object. A fresh process has none of these hazards, which is why the default is to rerun.

`exec` of a file's text and `runpy.run_path` both run the current source with no reload bookkeeping; the difference is where the assignments land. `exec` writes into the caller's namespace, so it can replace variables you were using; `run_path` gives the code its own namespace and returns it.
