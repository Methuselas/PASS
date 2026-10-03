---
object_id: PAT_use_a_dotted_from_import_for_sibling_modules_in_a_package
object_type: pattern
name: Use a Dotted from Import for Sibling Modules in a Package
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

# Use a Dotted from Import for Sibling Modules in a Package

## Pattern Rule
**IF** a module inside a package needs another module in that same package (or a parent package)
**THEN** reach it with a dotted `from` import — `from . import sibling`, `from .sibling import name`, `from .. import name` for the parent package — rather than a plain `import sibling`
**ELSE** when the target module lives outside this package entirely, use a plain `import` or `from` naming it by its full path from a directory on `sys.path`; that lookup was never relative to the package to begin with

## Do
- Use `from . import sibling` to fetch a module from the same directory as the file containing the statement; the single dot means "this package."
- Use `from .sibling import name` to copy one name out of that sibling module directly, same as any other `from` import once the sibling is located.
- Add additional leading dots to reach outward: `from .. import name` means "the parent of this package," `from ..sibling import name` means a module next to the parent package, and so on, one dot per level.
- Reserve this dotted syntax for `from` statements only; `import` has no relative form — `import sibling` always means an absolute search of `sys.path`, never the package's own directory.
- Use the full absolute path instead (`import mypkg.sibling`) when the same file must also work outside of any package context, or when the module might move and you'd rather update one `sys.path`-relative path than hunt down dots that assume a fixed position in the tree.

## Don't
- Don't write a plain `import sibling` inside a package file expecting it to find a module next to it; that statement only ever searches `sys.path`, and if nothing of that name exists there, the import fails even though the sibling module is sitting right next to the importing file.
- Don't use relative dotted syntax anywhere outside a file that is actually being imported as part of a package; it raises `ImportError: attempted relative import with no known parent package` the moment the containing file has no package context, including when the file is run directly as a script.
- Don't assume a relative import can reach above the top of the package currently being imported; `..` only resolves as far up as an actual importing package boundary exists, not past it.
- Don't let a module you plan to reach with `from . import x` be missing from the package directory and expect a fallback to some other `x` elsewhere on `sys.path`; relative import syntax is a binding declaration to the package directory, and finding nothing there is a hard failure, not a signal to search further.

## Checklist
- Is a sibling module being reached with a plain `import`, when a dotted `from` is what's actually needed?
- Does the dot count correctly reflect how many package levels to climb?
- Could the file containing this relative import ever run without a parent package context (direct execution, a one-off script)?
- Would an absolute `import mypkg.sibling` serve better here, because this file must also work stand-alone?

## Notes
A package's own directory is never searched automatically for a plain `import` or `from` statement; it is treated exactly like any other directory not on `sys.path`. The dotted syntax exists specifically to let a file request its own package directory (or an ancestor of it) explicitly, without depending on where that package happens to sit on the search path. See `PAT_prefer_import_or_an_explicit_from_list_over_from_star` for the underlying choice between `import` and `from` once the target module is actually located.
