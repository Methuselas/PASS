---
object_id: PAT_choose_a_regular_package_or_a_namespace_package
object_type: pattern
name: Choose a Regular Package or a Namespace Package
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
- __init__
cross_links:
- rel: related_to
  target_object_id: PAT_make_cross_directory_code_importable_with_a_package_not_path_hacks
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Choose a Regular Package or a Namespace Package

## Pattern Rule
**IF** turning a directory of modules into an importable package
**THEN** give it an `__init__.py` file (a regular package) whenever the package needs initialization code, a curated `from package import *` surface via `__all__`, or the fastest possible import resolution
**ELSE** leave `__init__.py` out (a namespace package) when the directory has no initialization work to do, or when the package's content is meant to be assembled from more than one physical directory at import time

## Do
- Add `__init__.py` — even empty — to any package that needs one-time setup (opening a connection, building a lookup table) the first time it's imported; its top-level code runs automatically, exactly once, the first time anything imports through that directory.
- Define `__all__` in `__init__.py` to control exactly what `from package import *` exposes; without it, a star-import only picks up names `__init__.py` itself assigns or explicitly imports, not every submodule in the directory.
- Treat a package without `__init__.py` as a legitimate, first-class package (a namespace package): it needs no special declaration, works with `import`, `from`, and relative imports exactly like a regular package once created, and is recognized automatically.
- Prefer a namespace package specifically when a logical package may be split across multiple install locations (a plugin system, a vendored extension to a larger package) — namespace packages are a virtual concatenation of every same-named directory found on the search path, which a regular package cannot be.
- Reach for a regular package when import speed matters and the package will never need to span directories: Python resolves a regular package as soon as its directory is found, while a namespace package's creation isn't finalized until the entire search path has been scanned with nothing else matching first.

## Don't
- Don't assume an empty `__init__.py` does nothing useful; its mere presence still declares the directory a package and stops it from being read as a namespace package, which matters if you specifically want the single-directory, immediately-resolved form.
- Don't expect `from package import *` to pull in every submodule automatically; without `__all__`, it only gets what `__init__.py`'s own code defines or imports — remaining submodules still need an explicit import.
- Don't put an `__init__.py` in any directory meant to participate in a namespace package; its presence there stops the namespace search immediately and that directory becomes an ordinary regular package instead, abandoning the multi-directory merge.
- Don't be surprised when a plain module file, or a regular package, beats a same-named namespace-package directory anywhere else on the search path; Python only falls back to assembling a namespace package after scanning the whole path and finding no file or `__init__.py`-bearing directory first.

## Checklist
- Does this package need to run code, or define `__all__`, the first time it's imported?
- Could this package's content ever need to be split across more than one install location?
- Is import-resolution speed a real constraint here, favoring the regular form?
- Does any directory meant to join a namespace package still have an `__init__.py` left in it?

## Notes
Both forms are real, current, and coexist in the same program: Python looks for a regular package first, then a plain module file, and only builds a namespace package out of every matching bare directory it found along the way if neither appeared. A namespace package's `__path__` lists every directory that contributed to it, and that composite path is then searched the same way `sys.path` is searched at the top level, so further nesting inside a namespace package works identically to nesting inside a regular one. See `PAT_make_cross_directory_code_importable_with_a_package_not_path_hacks` for getting a package's root itself onto the search path in the first place.
