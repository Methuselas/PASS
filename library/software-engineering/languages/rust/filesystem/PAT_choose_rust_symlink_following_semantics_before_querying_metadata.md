---
object_id: PAT_choose_rust_symlink_following_semantics_before_querying_metadata
object_type: pattern
name: Choose Rust Symlink-Following Semantics Before Querying Metadata
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
- symlink
- metadata
- paths
- security
cross_links:
- rel: related_to
  target_object_id: PAT_manipulate_rust_filesystem_paths_as_paths_not_strings
- rel: related_to
  target_object_id: PAT_start_with_portable_interfaces_then_isolate_platform_extensions
reference:
  source_title: Practical System Programming for Rust Developers
  author: Prabhu Eshwarla
confidence: medium
references: []
variants: []
---

# Choose Rust Symlink-Following Semantics Before Querying Metadata

## Pattern Rule
**IF** a Rust filesystem decision depends on metadata and the path may be a symbolic link
**THEN** decide whether the contract concerns the link itself or its target before choosing a metadata API, using symlink_metadata for the path entry and metadata when following the link is intended

## Do
- Use symlink-aware metadata when classifying or enforcing policy on the directory entry itself.
- Use target-following metadata only when the operation deliberately acts on the resolved target.
- Carry the same follow-versus-no-follow decision through recursive traversal and security-sensitive checks.
- Handle dangling links as a distinct outcome when the domain needs to preserve or report them.

## Don't
- Don’t call metadata and then expect FileType::is_symlink to identify the original path as a symlink.
- Don’t mix link identity and target identity in one policy check.
- Don’t assume symlink behavior or creation APIs are identical across operating systems.

## Checklist
- Is the policy about this directory entry or about the object it resolves to?
- Could following the link cross a trust, directory, or filesystem boundary?
- What should happen for a dangling or cyclic link?
- Are platform-specific symlink operations isolated behind the filesystem boundary?

## Notes
Symlink traversal changes what object a path-based operation observes. Making that choice explicit prevents classification bugs and keeps security-sensitive filesystem checks from silently switching from the link entry to an unexpected target.
