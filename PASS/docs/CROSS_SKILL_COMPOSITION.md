# Cross-Skill Composition by Auxiliary Fallback

Status: accepted architecture; PASS packaging and authority resolution implemented

Decision date: 2026-09-07

## Problem

A useful domain skill can require a narrow part of another domain in order to
produce acceptable work. Game Design, for example, may need adventure prose
from Writing and cartography from Art. A standalone Game Design archive cannot
assume that either owner skill is installed, that a shared repository exists,
or that the runtime has internet access.

Copying an entire foreign skill into every dependent release wastes the package
budget and exposes unrelated capabilities. Treating copied cards as new Game
Design cards breaks canonical ownership. Loading every installed copy creates a
different problem: two releases can carry different revisions of the same card,
leaving the model with competing instructions and no principled authority.

## Decision

PASS keeps one canonical owner for every card. A release recipe may select a
bounded, demonstrated closure from another domain as an **auxiliary fallback**.
The relationship is release metadata; it is not a new card type, lane, tag, or
frontmatter field.

In a shared `library/` checkout, the recipe resolves those cards in their owning
domain and does not create another canonical copy. In a portable release, the
builder materializes byte-identical copies at their canonical paths, such as
`library/writing/...` and `library/art/...`, together with their hard
prerequisites and local assets. The copies remain owned by Writing and Art.
Their auxiliary role exists only in `RELEASE_MANIFEST.json`.

This is controlled release duplication, not canonical duplication. It changes
neither the authoring boundary nor the relationship graph: cards may still
reference only their own domain and `metaskills`.

## Vocabulary

- **Owner domain:** the `library/<domain>/` package in which a card is authored.
- **Owner provider:** an available skill release that declares that domain as
  owned and can supply the complete compatible closure required by the task.
- **Auxiliary fallback:** a frozen release-local copy of a bounded closure from
  another owner domain.
- **Auxiliary group:** one release's complete fallback closure for one owner
  domain. Authority is selected for the group, never independently per card.

`Auxiliary` therefore answers “why is this card in this release?” It never
answers “what kind of card is this?”

## One active authority

Before cross-skill execution, the host or portable router resolves each required
owner domain from the manifests of the skills active for that task:

1. If exactly one owner provider supplies the complete compatible requirement,
   use it and suppress every auxiliary group for that owner domain.
2. If no complete owner provider is available, use the invoking release's
   auxiliary group.
3. If several active auxiliary groups supply the same object IDs with identical
   hashes, they may be coalesced as the same fallback.
4. If active auxiliary groups disagree on the bytes for any shared object ID,
   fail preflight. The runtime must not select the newest, the first loaded, or
   the copy belonging to an arbitrarily preferred skill.
5. If more than one active skill claims to own the same domain, fail preflight.
6. Never mix part of an owner provider with part of an auxiliary group. An
   incomplete or incompatible owner provider does not shadow the fallback.

A provider is compatible when it satisfies the required stable object IDs,
their complete hard-prerequisite closure, the applicable PASS release contract,
and required assets. Its card hashes may be newer than the fallback hashes. This
is how an installed Writing or Art skill supplies its current teaching without
forcing Game Design to be repackaged.

Only skills selected or discovered for the current task participate in this
preflight. Merely having an unrelated skill installed must not activate its
cards. A host that cannot discover another skill's manifest simply uses the
self-contained fallback; offline execution remains valid.

## Manifest contract

The portable contract is expressed in each release's existing
`RELEASE_MANIFEST.json`, not in a global registry. Manifest schema 2 records:

- `owned_domains`, derived from the recipe's primary modules;
- `object_ids`, the complete packaged card inventory used to qualify an owner
  provider;
- `auxiliary_groups`, with `domain`, recipe-selected `entry_object_ids`, resolved
  `object_ids`, canonical `owner_modules`, `object_paths`, and packaged `files`;
- the SHA-256 hashes already used to verify shipped files; and
- `pass_version`, used to decide compatibility.

The same manifest must support archive use, shared-library use, and safe import
into a consumer repository. Card contents must not be rewritten to encode the
role.

## Repository and archive behavior

The two deployment shapes use the same card/frontmatter contracts and the same
authority rule:

- A repository-style consumer resolves the recipe against cards in their
  canonical owner folders. It needs no physical auxiliary duplicate.
- A standalone archive carries the fallback files locally under those same
  canonical paths.
- Importing an owner release into a shared consumer repository may replace or
  shadow auxiliary files from that owner domain. Importing an auxiliary fallback
  must never downgrade an installed owner domain.
- Removing an owner release from a merged consumer repository can also remove
  the files that shadowed its fallbacks. Reinstalling the dependent release
  restores its packaged fallback. Manual deletion or unmanaged archive merging
  remains the consumer's responsibility.
- A release import must never overwrite the canonical PASS authoring library.

## How a recipe earns an auxiliary group

Recipes record demonstrated requirements; they do not guess at all capabilities
a domain might someday need.

1. Run a representative Drill or production evaluation against the candidate
   primary release.
2. Attribute each valid failure. A missing reusable decision points to a
   Pattern; a missing reusable sub-action or orchestration points to an AP.
3. Add the smallest justified entry object from the owning domain, then resolve
   its entire hard-prerequisite and asset closure.
4. Rerun the evaluation. Record the closure as **demonstrated sufficient**, not
   mathematically minimal, unless removal testing established minimality.
5. Requalify the recipe as the participating domains evolve.

Repeated ad-hoc Pattern chains or a growing list of fine-grained auxiliary
entries are evidence that the owner domain may lack a specialization AP—for
example, referee-facing adventure prose or game cartography. That AP is authored
and maintained in Writing or Art, then selected by the Game Design recipe. The
recipe is where finished domains meet; their authoring processes remain
independent.

Drills discover and verify composition. They ship only when the released product
offers practice or assessment; they do not travel merely because they were used
to qualify a recipe. The adventure evaluation completed before this decision
provides an initial Writing-and-Art candidate set, but it did not trace retrieval
or prove strict minimality, so that set is evidence rather than a normative
recipe.

## Skillset Memory

Auxiliary card presence does not bundle the foreign domain's Skillset Memory.
Memory is empirical, domain-scoped state and is not part of the executable card
closure. The first implementation continues to ship memory only for domains
owned by the release. Any future cross-skill memory composition requires a
separate explicit decision.

## Consequences

- Standalone releases remain useful without internet, MCP infrastructure, a
  shared checkout, or separately installed skills.
- Installing an owner skill supplies current cards without repackaging every
  dependent release.
- Portable releases contain only the foreign capabilities their evaluations
  justified, not entire unrelated domains.
- Old standalone fallbacks remain frozen until their dependent release is
  rebuilt. That is deliberate reproducibility, not synchronization failure.
- Conflicting fallback revisions become a visible preflight error instead of
  silent instruction contamination.
- Package size still grows with each fallback closure, so recipes must remain
  bounded and deployment limits still apply.

## Non-goals

This decision does not introduce cross-domain card references, a global
dependency database, online fetching, an always-on service, card mutation,
automatic domain maturity, or automatic synchronization between installed
archives. It does not decide the exact Game Design auxiliary list.

## Implementation boundary

As of the decision date, the recipe schema, builder, release checker, manifest,
generated skill router, and optional runtime authority resolver implement the
PASS-side contract. No production recipe selects an auxiliary group yet, so
`v1.0.0-beta.4` remains an honest historical release under the previous
contract.

Safe merged-repository installation/removal and host-specific discovery still
require qualification. No production recipe may adopt auxiliary entries until
tests prove no owner downgrade for its supported import path and smoke tests
prove discovery on the intended hosts. The current automated suite covers
canonical authoring isolation, byte-identical card and asset packaging, complete
card closure, foreign-memory exclusion, owner-provider precedence, whole-group
selection, identical-fallback coalescing, disagreement failure, multiple-owner
failure, and manifest/check integrity.
