---
object_id: PAT_choose_rust_links_by_file_identity_or_path_indirection
object_type: pattern
name: Choose Rust Links by File Identity or Path Indirection
library_path:
- software-engineering
- languages
- rust
- filesystem
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- rust
- filesystem
- hard-link
- symlink
- identity
- paths
cross_links:
- rel: related_to
  target_object_id: PAT_choose_rust_symlink_following_semantics_before_querying_metadata
reference:
  source_title: Practical System Programming for Rust Developers
  author: Prabhu Eshwarla
confidence: medium
references: []
variants: []
---

# Choose Rust Links by File Identity or Path Indirection

## Pattern Rule
**IF** Rust code needs another filesystem name for an existing object
**THEN** choose a hard link when the new name should identify the same underlying file, and choose a symbolic link when the new entry should store a pathname that is resolved later
**ELSE** avoid adding link semantics when copying, moving, or storing the target path directly expresses the real requirement

## Do
- Use `fs::hard_link` when both names can live on a filesystem that supports the operation and the new entry should continue to identify the same file object independently of the other name.
- Use a symbolic link when pathname indirection is intended, including cases such as cross-filesystem targets or directory targets where hard-link semantics are unavailable or inappropriate.
- Use the platform-appropriate symbolic-link API and `fs::read_link` when the program needs to inspect the stored target path.
- Decide separately whether later metadata operations should follow a symlink or inspect the link itself.

## Don't
- Don't expect a hard link to work across filesystems; systems commonly require both names to reside on the same filesystem.
- Don't expect a symbolic link to track a target that is renamed or moved; it stores a pathname, and that pathname can become dangling.
- Don't assume removing or renaming one hard-link name removes the underlying file while another hard link still names it.

## Checklist
- Should the new entry share file identity, or should it resolve a stored path?
- Can the target and new hard-link name satisfy the filesystem's hard-link restrictions?
- Must the link be able to name a directory or cross a filesystem boundary?
- What should happen if the target path is renamed, removed, or replaced?

## Notes
A hard link is another directory entry for the same underlying file, so another hard-link name can continue to reach that file after one name is renamed or removed. A symbolic link is a distinct filesystem object containing a path; resolution follows that path at access time, so moving the target can break it. That identity-versus-indirection distinction is the durable decision; platform APIs and restrictions are implementation details around it.
