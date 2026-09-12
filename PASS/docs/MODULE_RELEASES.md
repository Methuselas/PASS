# Module and Release Composition

A source module owns coherent reusable knowledge and declares only local direct
requirements in `MODULE.yaml`. A named release recipe selects its entry module(s).
`build_release.py` always adds `metaskills`, recursively resolves module and object
prerequisites, runs the release quality gates, then materializes the complete
closure under `library/` inside the release.

A recipe's primary `modules` are one owned domain plus the shared `metaskills`
package. Their module and object closure stays inside that domain. A recipe may
also select bounded foreign-domain card closures as auxiliary fallbacks while
preserving canonical domain ownership and the prohibition on cross-domain card
references. The authority, conflict, Drill, and memory rules are normative in
[`CROSS_SKILL_COMPOSITION.md`](CROSS_SKILL_COMPOSITION.md).

Auxiliary entries use stable object IDs grouped by their canonical owner domain:

```yaml
modules:
  - game-design/adventures
auxiliary:
  - domain: writing
    objects:
      - writing_ap_revise_creative_draft_from_diagnosis_to_final_proof
  - domain: art
    objects:
      - AP_project_plan_and_elevation_into_perspective
```

The example demonstrates syntax only; those entries are not a qualified Game
Design recipe. `auxiliary` is optional. Each domain may occur once, every entry
must belong to the declared foreign domain, and an owned domain cannot also be
auxiliary. Unknown keys, duplicate domains or objects, missing IDs, and ownership
mismatches fail before materialization.

The builder resolves each auxiliary entry at card granularity through
`foundation_object_id`, every canonical `cross_links` target, and the reverse
side of `prerequisite_for`. It copies those canonical card bytes, declared assets
and review sidecars under their original `library/<domain>/...` paths. It does
not copy the foreign domain's canonical `MODULE.yaml`; instead, the release
manifest records each card's owner module. Release-local indexes are regenerated
from the cards that actually ship.

The release preserves canonical `library/...` paths. This is deliberate: trained
cards may contain local asset paths such as `library/art/.../assets/foo.png`, and
those paths must continue to resolve after export without rewriting card content.
Missing assets fail the build and `check` command.

Every release root is an Agent Skills-compatible directory. `SKILL.md` contains
required YAML `name` and `description` metadata followed by compact routing
instructions. Profile-owned execution barriers live in the conditional
`references/execution-barriers.md`; the complete declarative contract remains in
`runtime/profile.yaml`. The same release can be uploaded/installed where Agent
Skills are supported or used directly as an archived/context package.

`RELEASE_MANIFEST.json` records the Semantic Versioning value from the factory's
root `VERSION` file as `pass_version`. This identifies the PASS schema, tooling,
snapshot/import, runtime, and release contract that produced the package; it is
not the independent product version of the selected SkillForge skillset. Its
`drill_runner` boolean records whether the resolved object set contains a Drill
and therefore carries the portable administrator.

When the resolved object set contains at least one canonical Drill, the builder
also vendors `scripts/skillforge_drill.py`. This is derived from card frontmatter,
not a domain registry: future domains inherit the same administration substrate
by shipping valid Drill cards. Releases without Drills do not carry it.

Every release also carries `LICENSE.md`, `NOTICE.md`, `TRADEMARKS.md`,
`CONTRIBUTING.md`, and the complete license texts under `LICENSES/`. The vendored
Python helpers are `AGPL-3.0-or-later`; Skill instructions, cards, declarative
profiles, memory, and original assets are `CC-BY-SA-4.0` unless a shipped file
states otherwise. A release missing any licensing or attribution file fails
`build` and `check`.

## Skillset Memory in a release

A release ships the memory store of every domain owned by its primary modules,
and no other. The domain is the top-level package name of a selected module, so
`art/composition` and
`art/subjects/animals` both mean `memory/art/`. Stores land at
`memory/<domain>/` in the release root — beside `library/`, never inside it.
Packaging memory must not turn an observation into a card (`ARCHITECTURE.md`
contract 20).

Auxiliary cards do not cause their owner domain's memory to ship. Cross-skill
memory composition is outside the accepted decision and requires separate
authorization.

Memory is not a build dependency. A domain with no store contributes nothing,
and a build with `memory/` deleted entirely succeeds and declares
`memory_domains: []`. `--memory` overrides the tree the stores are read from;
it receives the same output protection as `--library`.

Shipped memory files are written read-only, and the ZIP carries both the POSIX
mode and the DOS read-only attribute so either extractor preserves it. The
release is a reader of the record, not its persistence target: new events belong
to the library that owns the store. Read-only is a statement of that contract,
not a security boundary — a consumer who clears the bit only forks a copy that
no longer travels back.

`RELEASE_MANIFEST.json` records the shipped domains in `memory_domains`, and
`check` rejects a declared domain whose store is missing, a packaged domain the
manifest does not declare, and a memory domain with no matching packaged library
package.

## Quality gate

A normal release build fails closed unless all of these pass:

1. the root Semantic Version is documented and `Unreleased` contains no
   substantive notes;
2. PASS schema and relationship validation;
3. visual-reference asset verification;
4. local asset resolution;
5. portability scan;
6. Skillset Memory validation, when the release ships a store.

Every gate runs against the materialized release closure, so a release is
publishable on the strength of the cards it actually ships and a defect in an
unrelated skill family cannot block an independent release.

A release build never resolves research provenance. It cannot fail because a
source PDF is missing, an attestation is stale, a ledger is absent, or another
domain was not inspected — none of those exist. Retired 2026-08-15.

`--unsafe-skip-quality-gates` exists only for composition fixtures/tests. A release
built that way is marked unsafe and intentionally fails `build_release.py check`.

## Output safety

The builder never recursively deletes an existing directory by default. Existing
outputs require `--replace`, and release outputs inside or above the factory
repository are refused even with that flag. Explicit external library, memory, and
recipe paths receive the same ancestor/descendant protection. Builds occur in a temporary
sibling directory and are moved into place only after validation succeeds.

ZIP output remains opt-in.

Each release manifest records a SHA-256 digest for every shipped file other than
the manifest itself. `build_release.py check` rejects missing, changed, or
unexpected files, missing or undeclared modules, unresolved packaged object
relationships, missing licensing or attribution notices, and stale quality-gate
state. ZIP targets use the same canonical path protection as release directories
and must use a `.zip` extension.

Release closure follows every outgoing canonical `cross_links` target and the
reverse side of `prerequisite_for` edges, in addition to module requirements and
`foundation_object_id`. This keeps the packaged object graph self-contained;
soft relationships such as `related_to`, `supports`, and `teaches` may not turn
into dangling links merely because their target lives in another module.
