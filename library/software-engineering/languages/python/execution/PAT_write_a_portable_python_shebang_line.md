---
object_id: PAT_write_a_portable_python_shebang_line
object_type: pattern
name: Write a Portable Python Shebang Line
library_path:
- software-engineering
- languages
- python
- execution
stage_binding: 4 final
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- scripts
- shebang
- portability
cross_links: []
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Write a Portable Python Shebang Line

## Pattern Rule
**IF** a Python file is meant to be run directly as a command — `./tool` on Unix-like systems, or by name through the Windows `py` launcher
**THEN** make its first line `#!/usr/bin/env python3` (or `python3.X` when it truly needs one version) and mark it executable, so the interpreter is found through the user's `PATH` instead of a path baked into the file
**ELSE** when the file is only ever imported or run as `python file.py`, leave the line out; it is a comment to Python and does nothing there.

## Do
- Put the shebang on the very first line, before any comment, docstring or encoding declaration.
- On Unix-like systems, give the file execute permission (`chmod +x tool`) and run it as `./tool`, or from any directory once its folder is on `PATH`.
- Name `python3` rather than `python`: on many systems `python` is absent or is not a Python 3 interpreter.
- Keep the `.py` suffix on files that other code imports; a runnable command may drop the suffix, but an importable module may not.
- On Windows, run the file with `py tool.py`: the launcher reads a `/usr/bin/env python3.X` shebang and starts the matching installed Python, so one file carries its version choice on both platforms.

## Don't
- Don't hardcode an interpreter path such as `#!/usr/local/bin/python`; it breaks on every machine or virtual environment where Python lives somewhere else.
- Don't expect the shebang to matter when the file is imported or passed to `python` explicitly; only direct execution (and the Windows `py` launcher) reads it.
- Don't rely on the Windows shell itself honoring the line: Command Prompt picks the program for a `.py` file from its file association, not from the first line.

## Checklist
- Is `#!/usr/bin/env python3` (or a specific `python3.X`) exactly on line 1?
- Is the file marked executable where it will be run directly?
- Does it run as `./tool` from a fresh shell, and as `py tool.py` on Windows?

## Notes
The shebang is an operating-system convention, not Python syntax: to Python the line is an ordinary comment. The `env` form hands the search to the environment, so the same file runs under whatever `python3` comes first on `PATH` — a system install, a user install, or an activated virtual environment — and a moved interpreter means updating `PATH`, not every script. The one assumption left is that `env` itself lives at `/usr/bin/env`, which holds on mainstream Unix-like systems.
