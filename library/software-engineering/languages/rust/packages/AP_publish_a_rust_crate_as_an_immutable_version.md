---
object_id: AP_publish_a_rust_crate_as_an_immutable_version
object_type: ap
name: Publish a Rust Crate as an Immutable Version
library_path: [software-engineering, languages, rust, packages]
stage_binding: 4 final
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, cargo, crates_io, publishing, semver, release]
cross_links:
- rel: supports
  target_object_id: PAT_state_your_compatibility_promise_and_its_span
- rel: supports
  target_object_id: PAT_make_rust_documentation_examples_executable
- rel: supports
  target_object_id: PAT_keep_cargo_workspace_members_dependency_explicit
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
references: []
variants: []
---

# Publish a Rust Crate as an Immutable Version

## Objective

Publish exactly the reviewed Rust crate contents and metadata as a new immutable registry version. Success means the registry artifact, not merely the working tree, passes the required verification and the release record identifies exactly what downstream users can resolve.

## Steps / Flow

1. **Establish the release entry state.** Begin with a reviewed source tree, a clean package selection, registry authorization through an approved credential or trusted-publishing path, and passing tests under the supported features, targets, and toolchain policy. Keep credentials out of source, scripts, logs, and shell history.

2. **Classify compatibility before choosing the version.** Apply `PAT_state_your_compatibility_promise_and_its_span` to the actual public change, then choose a registry version that has never been published. Do not let the desired version number decide whether the change is compatible.

   *Gate.* Stop if the compatibility impact, package name, version, license expression or license file, description, repository links, or other required metadata is unresolved.

3. **Inspect the deliverable Cargo will package.** Review the packaged file list and correct include or exclude rules, generated-file omissions, secret exposure, and accidental repository artifacts. The working directory is not the release artifact.

4. **Verify from the package archive.** Build the archive and use Cargo's package verification path so its compilation check runs against packaged contents rather than only the working tree. Separately run the package's required tests and inspect rendered public documentation; `PAT_make_rust_documentation_examples_executable` owns the requirement that published examples compile and behave as claimed.

   *Recovery.* If packaging, archive verification, documentation, or another release gate fails, repair the source or manifest and rebuild the archive from the beginning. Never publish a different artifact from the one inspected.

5. **Order workspace publications by their explicit dependency graph.** Apply `PAT_keep_cargo_workspace_members_dependency_explicit`: select the intended package rather than treating workspace membership as publication, give every registry dependency a valid version requirement, and publish dependencies before dependents. Stop if a publishable member still resolves a sibling only through a local path.

6. **Publish the exact new version once.** Target the intended registry explicitly when the configuration admits more than one, and publish with the approved authentication mechanism. If the registry rejects the request, distinguish name, metadata, version collision, dependency, authorization, and registry-policy failures before retrying; do not respond to every rejection by changing the version.

7. **Verify the registry artifact downstream.** Confirm that the registry exposes the expected version, metadata, documentation link, checksum, and dependency requirements. For a binary crate or release-critical library, install or resolve it from the registry rather than from a local path.

8. **Record evidence and handle post-publication failure by moving forward.** Record the published version, source revision, package checksum or archive evidence, commands or CI job, and validation results. A published version is immutable: if it is defective, yank it when new resolutions should avoid it, notify affected consumers, and publish a corrected higher version. If it exposed a secret, revoke and rotate the secret immediately; yanking cannot make published bytes secret again.

9. **Completion check.** Finish only when the intended immutable version is available from the registry, its packaged contents and metadata match the reviewed release, required downstream consumption succeeds from the registry artifact, and the release record identifies exactly what was published.

## Notes
Registry publication is an external, durable state change. The package archive—not the developer's working directory—is the deliverable, and recovery after publication is a forward version or resolution control rather than replacement of the existing version.
