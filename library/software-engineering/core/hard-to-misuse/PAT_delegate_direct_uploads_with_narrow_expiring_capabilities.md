---
object_id: PAT_delegate_direct_uploads_with_narrow_expiring_capabilities
object_type: pattern
name: Delegate Direct Uploads With Narrow Expiring Capabilities
library_path:
- software-engineering
- core
- hard-to-misuse
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: general
specialization_axis: none
foundation_object_id: PAT_treat_uploaded_files_as_untrusted_content_and_paths
tags:
- uploads
- capabilities
- least_privilege
- object_storage
- security
cross_links:
- rel: related_to
  target_object_id: PAT_barricade_dirty_data_at_a_named_boundary
- rel: related_to
  target_object_id: PAT_separate_external_write_models_from_stored_entities
reference:
  source_title: Practical Rust Web Projects
  author: Shing Lyu
confidence: medium
references: []
variants: []
---

# Delegate Direct Uploads With Narrow Expiring Capabilities

## Pattern Rule
**IF** an untrusted client should upload a large object directly to storage without receiving the backend's storage credentials
**THEN** have the trusted backend authorize the request and mint a short-lived capability constrained to the intended operation and a server-selected destination, then continue to treat the uploaded object as untrusted until validation and publication policy complete
**ELSE** when the backend must inspect or transform the entire body before storage and the extra hop is acceptable, receive the upload through that trusted boundary instead

## Do
- Authenticate and authorize before issuing the capability; possession of the capability should not replace the decision about whether the caller may upload.
- Choose the destination on the trusted side and use collision-resistant or otherwise deliberate naming so a caller cannot redirect the capability or silently overwrite an unrelated object.
- Restrict the capability to the minimum operation, destination, lifetime, and additional integrity, size, or content constraints the storage system can enforce.
- Keep newly uploaded objects outside the trusted or public set until content validation, malware or format checks, and any required transformation have completed.
- Define what reconciles an abandoned, expired, duplicate, or partially completed upload so delegated transfer does not create permanent orphan state.

## Don't
- Don't give a browser or other untrusted client the backend's general storage credentials merely to avoid proxying bytes through the application.
- Don't let the client choose an arbitrary storage key or path that the backend then signs without applying the server's naming and authorization policy.
- Don't assume short-lived means single-use; a capability may remain reusable until expiry unless the underlying mechanism provides stronger replay controls.
- Don't treat successful direct storage as proof that the bytes are safe to publish or consume.
- Don't use a predictable destination when overwriting an existing object would be harmful and the storage operation permits replacement.

## Checklist
- Who authorizes the upload before the capability is minted?
- Exactly which operation, destination, and lifetime does the capability permit?
- Can the capability be replayed or can the chosen key replace an existing object?
- What validation must succeed before the object is trusted or publicly served?
- What cleans up uploads that are issued but never completed, or completed after the surrounding application operation fails?

## Notes
A signed upload URL or equivalent token is best understood as a delegated capability, not as a substitute for upload validation. It solves a credential and data-path problem: the client can transfer bytes directly to storage without holding broad backend authority. The trust boundary from the upload pattern still remains. Server-selected naming, narrow authority, short lifetime, and a quarantine-to-publication step keep the optimization from widening what the client is allowed to control.
