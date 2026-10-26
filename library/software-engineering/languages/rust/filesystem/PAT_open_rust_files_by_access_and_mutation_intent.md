---
object_id: PAT_open_rust_files_by_access_and_mutation_intent
object_type: pattern
name: Open Rust Files by Access and Mutation Intent
library_path:
- software-engineering
- languages
- rust
- filesystem
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- rust
- filesystem
- file
- openoptions
- truncate
- append
cross_links:
- rel: related_to
  target_object_id: PAT_keep_rust_failures_as_result_until_recovery_context_exists
reference:
  source_title: Practical System Programming for Rust Developers
  author: Prabhu Eshwarla
confidence: medium
references: []
variants: []
---

# Open Rust Files by Access and Mutation Intent

## Pattern Rule
**IF** Rust code opens a filesystem path and existing contents may matter
**THEN** choose `File::open`, `File::create`, or `OpenOptions` from the required read/write/create/truncate/append semantics before touching the file
**ELSE** use the narrow convenience operation whose destructive behavior is already part of the intended contract

## Do
- Use `File::open` when the operation requires an existing file opened for reading.
- Use `File::create` only when creating the file if absent and truncating an existing file to length zero are both acceptable.
- Use `OpenOptions` when the operation needs a different combination of read, write, create, truncate, or append behavior.
- Use append semantics when new bytes must be added to the end without replacing the existing contents.

## Don't
- Don't use `File::create` as a generic way to obtain a writable handle when existing contents must survive; an existing file is truncated.
- Don't treat `create(true)` as a complete write policy; decide separately whether existing bytes should be preserved, overwritten, truncated, or appended to.
- Don't hide the open policy behind a helper whose name does not reveal destructive behavior at a call site where data preservation matters.

## Checklist
- Must the path already exist, may it be created, or must creation fail when it already exists?
- If the file exists, may its current contents be destroyed?
- Is writing supposed to replace bytes, truncate first, or append at the end?
- Does the chosen API make that policy visible before the first write occurs?

## Notes
Rust's convenience constructors encode policy. `File::open` is read-only and expects the path to exist; `File::create` is write-only, creates when absent, and truncates when present. `OpenOptions` is the explicit path when the required mutation contract does not match either convenience case. The important decision is made at open time, before an accidental truncate can be recovered from.
