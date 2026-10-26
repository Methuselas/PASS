---
object_id: PAT_walk_rust_directory_trees_with_entry_policies
object_type: pattern
name: Walk Rust Directory Trees with Entry Policies
library_path: [software-engineering, languages, rust, filesystem]
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, filesystem, walk, hard_links, symlinks, error_handling]
cross_links:
- rel: related_to
  target_object_id: PAT_choose_rust_links_by_file_identity_or_path_indirection
- rel: related_to
  target_object_id: PAT_choose_rust_symlink_following_semantics_before_querying_metadata
- rel: related_to
  target_object_id: PAT_guard_rust_filesystem_probes_before_unwrapping
reference: {source_title: Practical System Programming for Rust Developers, author: Prabhu Eshwarla}
confidence: medium
references: []
variants: []
---

# Walk Rust Directory Trees with Entry Policies

## Pattern Rule
**IF** Rust code recursively walks directories to collect files or compute aggregates
**THEN** decide before traversal whether results are counted per pathname or per underlying file identity, whether symbolic links are followed, and how per-entry errors affect the final result.

## Do
- State whether two hard-link names count as two path entries or one underlying file. Deduplicate by file identity when content-based totals must not double-count aliases.
- Choose symlink behavior deliberately. If directory symlinks are followed, carry a visited-identity policy so a link cycle cannot recurse forever.
- Handle each `read_dir` item as a `Result`; propagate, report-and-skip, or accumulate failures according to the tool's completeness contract.
- Derive aggregate counts from the same accepted entry set used for the actual work so summary numbers cannot drift from the processed files.

## Don't
- Don't assume one pathname equals one physical file when hard links are possible.
- Don't silently discard entry-level errors in a metrics or inventory tool; that produces plausible but incomplete totals.
- Don't mix target-following and no-follow metadata calls accidentally while deciding whether an entry is a directory or link.

## Checklist
- Are counts per name or per underlying file identity?
- Are symbolic links followed, ignored, or reported as their own entries?
- What prevents cycles if directory links are followed?
- Does an unreadable or vanished entry abort, warn, or get counted as skipped?
- Are totals computed from exactly the entries that passed the walk policy?

## Notes
The source's directory tools combine `read_dir`, path classification, link operations, and aggregate metrics. Those examples expose a durable boundary: traversal is not just recursion; it is a set of identity, link-following, and error policies that determine whether the final aggregate means what the caller thinks it means.
