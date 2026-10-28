---
object_id: PAT_treat_uploaded_files_as_untrusted_content_and_paths
object_type: pattern
name: Treat Uploaded Files as Untrusted Content and Paths
library_path:
- software-engineering
- core
- hard-to-misuse
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: general
specialization_axis: none
foundation_object_id: PAT_barricade_dirty_data_at_a_named_boundary
tags:
- file_upload
- untrusted_input
- path_safety
- content_validation
- security
cross_links:
- rel: related_to
  target_object_id: PAT_barricade_dirty_data_at_a_named_boundary
reference:
  source_title: Practical Rust Web Projects
  author: Shing Lyu
confidence: medium
references: []
variants: []
---

# Treat Uploaded Files as Untrusted Content and Paths

## Pattern Rule
**IF** a system accepts files from an untrusted client
**THEN** validate the permitted content independently of client-supplied metadata and map it to a server-controlled storage name and destination before making it available

## Do
- Treat the original filename, extension, MIME declaration, and path components as untrusted input.
- Enforce an allowlist appropriate to the application and inspect the actual content rather than trusting the filename alone.
- Generate or normalize the stored name so user-controlled path syntax cannot escape the intended storage location or overwrite an unrelated file.
- Keep malware scanning, size limits, decompression limits, and serving policy proportional to the threat model and file types accepted.

## Don't
- Save an uploaded file directly into a publicly served directory under the client-provided name.
- Treat an allowed extension as proof that the bytes have the claimed format.
- Let name collisions silently replace existing files.
- Expose uploaded content before validation and storage policy have completed.

## Checklist
- Which file types are actually allowed, and how is content verified?
- Can any supplied name or path component escape the intended destination?
- Can an upload overwrite an existing object?
- What size, malware, decompression, and serving controls apply before the file is trusted?

## Notes
A file upload crosses two independent trust boundaries: what the bytes contain and where the server stores or serves them. Treating only the filename or only the content as untrusted leaves the other boundary open.
