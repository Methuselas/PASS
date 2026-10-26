---
object_id: PAT_guard_rust_filesystem_probes_before_unwrapping
object_type: pattern
name: Guard Rust Filesystem Probes Before Unwrapping
library_path: [software-engineering, languages, rust, filesystem]
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, filesystem, path, metadata, unwrap, toctou]
cross_links:
- rel: related_to
  target_object_id: PAT_manipulate_rust_filesystem_paths_as_paths_not_strings
- rel: related_to
  target_object_id: PAT_keep_rust_failures_as_result_until_recovery_context_exists
reference: {source_title: Practical System Programming for Rust Developers, author: Prabhu Eshwarla}
confidence: medium
references: []
variants: []
---

# Guard Rust Filesystem Probes Before Unwrapping

## Pattern Rule
**IF** Rust code derives path components or metadata from user-supplied or enumerated filesystem paths
**THEN** keep the `Option` and `Result` boundaries explicit, because a valid path can lack the requested component and a directory entry can disappear or change between enumeration and later metadata access.

## Do
- Handle `file_name`, `file_stem`, `parent`, and similar optional components according to the domain: skip, return a structured error, or use another representation when the component is not present.
- Treat metadata lookup after enumeration as a fresh fallible operation. A file may be deleted, renamed, replaced, or made inaccessible after `read_dir` produced its entry.
- Decide which per-entry failures abort the entire operation and which are reported and skipped; make aggregate results reflect that policy.
- Preserve the underlying I/O error when mapping it into a domain error so the caller can distinguish disappearance, permission failure, and other causes.

## Don't
- Don't `unwrap` path components merely because the path string looked ordinary; paths such as `..` do not provide every file-oriented component.
- Don't `unwrap` metadata from an earlier directory listing as if the listing locked the filesystem state.
- Don't silently discard `read_dir` entry errors when a complete listing is part of the result contract.

## Checklist
- Can any path-component query return `None` for an input the program accepts?
- What happens if an entry vanishes between enumeration and metadata access?
- Are skipped entries observable when they affect counts or other aggregates?
- Does the error mapping preserve the original I/O cause?

## Notes
The source uses `read_dir`, path-component accessors, and later metadata queries in file-processing tools. Those APIs deliberately expose absence and I/O races through `Option` and `Result`; converting them to `unwrap` turns ordinary filesystem change into a process-wide panic.
