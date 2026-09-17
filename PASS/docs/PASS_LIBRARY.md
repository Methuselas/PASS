# PASS — Skill Library Contract

status: active
owner: docs/PASS_LIBRARY.md
notes: Defines portable module placement and release composition. `PASS_SCHEMA.md` remains the source of truth for object shape.

## Purpose

The library is a human-browsable source tree for reusable skill knowledge. The source tree is not automatically the shipping boundary. PASS composes source modules into complete self-contained releases.

## Placement

Every object owns its location through `library_path`.

```yaml
library_path: [art, drawing, subjects, figure, construction]
```

belongs at:

```text
library/art/subjects/figure/construction/
```

`library_path` is navigation and ownership. It must match the object's actual directory. It is not a hidden dependency system; prerequisites remain explicit in object relationships.

Typical durable paths include:

```text
library/metaskills/
library/software-engineering/core/
library/software-engineering/languages/cpp/
library/art/perspective/
library/art/subjects/figure/anatomy/
library/art/subjects/animals/anatomy/
library/writing/foundations/
```

Do not create empty future taxonomy merely to anticipate a domain that has not yet been authored or taught.

## Modules

A source module is a coherent reusable package of knowledge identified by a local `MODULE.yaml`.

```yaml
name: software-engineering/languages/cpp
requires:
  - software-engineering/core
```

A module under `languages/` requires its domain's language-agnostic `core`, and
`validate.py` enforces it. The requirement is one hand-written line; without the
check, a module that omits it still builds, and ships a release whose cards assume
a foundation the package does not contain.

Module metadata is local. PASS does not require a global module registry.

### Software core and language compatibility

Software Engineering `core` cards are language-agnostic decisions, not C++ cards
and not automatically verified in every language. Keep one canonical core owner.

When creating or extending a language module from instructional books, review
the relevant existing core Patterns, APs and Drills against each book's actual
language instruction. Select core owners per instructional unit, not by a
whole-core prerequisite sweep. Check their assumptions, actions and examples
against the declared language version and the new language cards. Exercise
executable claims with valid and misuse/boundary cases on the target toolchain;
assess design judgments against the book's real examples and constraints, not
compiler success alone. A module dependency or schema pass is not compatibility
evidence. Human-code field tests supplement this book-driven review; they do not
replace it.

Put language syntax, idioms and necessary exceptions in the language module.
Repair a falsely universal core claim at its existing owner; never fork core per
language or turn the shared decision into one language's implementation. Report
which core decisions were checked, which required specialization or repair, and
which remain unverified. Keep this account in the bounded run/delta report, not a
new registry, coverage database or source locator on a card. Authoring review is
not an empirical qualification or a requirement imposed on ordinary users.

A folder and a module are not required to be the same granularity. If two navigation folders contain mutually dependent knowledge, they may live inside one larger source module rather than creating an artificial module cycle.

## Object identifiers

`object_id` is required to be stable and unique library-wide. The schema constrains
nothing else about its shape. Writing now uses the same type-prefixed identifiers
as the other packages, matching each card's filename stem.

```text
type prefix
                       PAT_build_gesture_into_clear_masses
                       DRILL_make_a_function_exception_safe
                       AP_review_code_you_did_not_write
```

**Never infer an object's type from the shape of its id.** Other identifier shapes
remain valid under the schema. Resolve the id and read `object_type`, or read the
type from the filename.

Filenames are the uniform signal. Rule 9 requires the `PAT_` / `DRILL_` / `AP_`
prefix on every card in every package, so the path always says what an object is
even where the id says it differently.

## Object prerequisites

Hard prerequisites are independent of folder placement.

- `foundation_object_id` identifies a required foundation object.
- `cross_links` with `rel: prerequisite_for` identify hard prerequisite direction.
- Release composition follows these relationships recursively.
- If a required object cannot be found, export fails.
- Folder adjacency never substitutes for an explicit prerequisite.

## Mandatory metaskills

Every SkillForge release includes the `metaskills` module automatically. A release recipe does not need to remember to request it.

The metaskill is the universal process baseline. Domain modules extend it; they do not replace it.

## Independent skill domains

Every package under `library/` other than `metaskills` is an independent lane.
Each is authored and validated without the others, and its canonical package
build remains independent. A named product release may compose finished material
only through the bounded auxiliary-fallback contract. A card may reference other
cards in its own package, plus `metaskills`; any other cross-package reference is
a domain coupling and fails validation.

Instructional knowledge stays in the domain it belongs to. `lane_fit: teach`
marks a card as instructional within its own domain — it does not route the card
anywhere else and requires no shared Teaching package.

The former top-level `teaching` package was retired from the shared pipeline on
2026-08-15 and quarantined under `archive/teaching/`. Nothing active depends on
it. If Teaching is ever built properly, it becomes its own independent domain.

## Named releases

A named release selects the intended entry module or modules, not a hand-maintained copy of the full dependency closure.

```yaml
name: Animal Anatomy
modules:
  - art/subjects/animals
```

PASS then materializes:

1. the requested entry modules;
2. direct module requirements;
3. recursive module requirements;
4. modules containing hard object prerequisites;
5. `metaskills`.

The resulting release contains all selected material locally.

## Release boundary

A finished release may contain only material required to use the skill. It must not depend on the authoring workspace.

Do not ship:

- `.git`, `.agents`, or `.claude`;
- source PDFs, books, or other study material;
- authoring scratch notes;
- workspace-only tooling;
- build caches;
- unrelated skill families (a bounded auxiliary fallback demonstrated under
  [`CROSS_SKILL_COMPOSITION.md`](CROSS_SKILL_COMPOSITION.md) is related release
  material recorded in the release manifest);
- absolute paths or `../` dependencies back into PASS.

The workspace is the factory. The release is the product.

## Indexes

Indexes are optional generated navigation aids. They are not canonical architecture, a registry, or a dependency mechanism. If an index exists, regenerate it from the source objects rather than hand-maintaining it as a second source of truth.

## Authoring modes

Library structure does not decide how a skill is learned.

- Autonomous authoring may be used when sources and validation are sufficient.
- Human-guided authoring is used when durable behavior depends on formal teaching, interpretation, correction, or taste.

Do not flatten human-taught knowledge back into an autonomous source summary during maintenance.
