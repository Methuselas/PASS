---
object_id: PAT_make_cross_directory_code_importable_with_a_package_not_path_hacks
object_type: pattern
name: Make Cross-Directory Code Importable with a Package, Not Path Hacks
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
- packaging
- sys-path
cross_links: []
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Make Cross-Directory Code Importable with a Package, Not Path Hacks

## Pattern Rule
**IF** your own code needs to import from a directory other than the ones Python already searches automatically (the script's own directory, the standard library)
**THEN** install your code as a package — an editable install (`pip install -e .` from a project with a `pyproject.toml`) into a virtual environment is the current default — so it lands on `sys.path` through the interpreter's normal site-packages mechanism
**ELSE** for a one-off script, a REPL session, or a process that cannot assume packaging was ever run (a web handler executing as a locked-down system account, for instance), set `PYTHONPATH` or append to `sys.path` directly as a narrower, script-local fix

## Do
- Reach for a proper package (`pyproject.toml`, a src/ or flat layout, an editable install) as the default for any project spanning more than one directory of your own code; this is current Python packaging guidance, not merely one option among equals.
- Use a virtual environment per project, so each project's installed packages — including your own, installed editably — land on that interpreter's `sys.path` without touching any other project on the machine.
- Fall back to `PYTHONPATH` (an environment variable listing directories, searched after the script's home directory) only when packaging genuinely is not available: a quick personal script, a constrained deployment environment, a REPL experiment.
- Reach for `sys.path.insert(0, dir)` only inside a program that cannot rely on environment configuration at all, and do it exactly once, near the entry point, before any of the affected imports run.
- Inspect `sys.path` directly (`import sys; sys.path`) when an import fails unexpectedly or resolves to the wrong file; it is the authoritative, ordered list of directories actually searched.

## Don't
- Don't scatter `sys.path.append`/`sys.path.insert` calls across a codebase as the normal way to reach your own other directories; each call is a hidden, load-order-dependent dependency that an installed package does not need.
- Don't rely on the current working directory for imports in a deployed program; it is only part of the search path in some configurations, and it is whatever directory the process happened to be launched from, not a property of your code's layout.
- Don't let a same-named module sitting in the script's own home directory silently shadow a standard-library or installed module of the same name; the home directory is searched first, before everything else.
- Don't write or follow setup instructions built on `distutils`; it was removed from the standard library in Python 3.12, and the ecosystem now builds packages with `setuptools`, `hatchling`, `pdm-backend`, or another PEP 517 build backend driven by `pyproject.toml`.

## Checklist
- Does this project have a `pyproject.toml` and an editable or regular install, rather than relying on `PYTHONPATH` or runtime `sys.path` edits?
- Is each project using its own virtual environment?
- If `sys.path` is modified at runtime, does exactly one place do it, near the entry point, before the affected imports?
- Does any setup script or documentation here still reference `distutils` directly?

## Notes
The underlying search path — home directory, `PYTHONPATH`, standard library, `.pth` files, `site-packages` — hasn't changed in kind across Python versions; what changed is which layer current practice expects a developer to touch directly. An editable install writes a `.pth`-style entry (or a comparable import hook, depending on the build backend) into the environment's `site-packages` automatically, using the same mechanism `PYTHONPATH` and a hand-written `.pth` file use manually — packaging just makes the result reproducible and scoped to one environment instead of one shell session or one whole machine.
