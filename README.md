# PASS — Durable skillsets built from studied knowledge

PASS (Pattern Analysis Skill System) is an authoring, validation, and packaging
system for AI skills. It turns books, courses, documents, code, visual material,
and formal human teaching into small, reusable knowledge cards that still work
after the original source is gone.

PASS is not a document search system and it is not a folder of prompts. It is a
factory for building skillsets with explicit decisions, procedures, practice,
dependencies, runtime routing, validation, memory, project workspaces, and
self-contained releases.

**Project status:** public beta, version `1.0.0-beta.5`. The complete authoring,
validation, project-snapshot, and release workflows are available for public
use. Beta releases may still make documented compatibility corrections before
the stable `1.0.0` contract.

Finished, installable skillsets are published separately in
[SkillForge](https://github.com/Methuselas/The_Skill_Forge). PASS is the authoring
factory; SkillForge is the distribution repository.

```text
SOURCE OR HUMAN TEACHING
        ↓ study one coherent instructional unit
PATTERNS + APs + DRILLS
        ↓ validate, relate, and mature
DOMAIN LIBRARY + SKILLSET MEMORY
        ↓ assemble for the job
PROJECT FOLDER / PROJECT ZIP / INSTALLABLE RELEASE
```

The central rule is simple: **a finished card must remain valid and executable
after its source is gone.** Cards do not depend on source paths, page numbers,
receipts, hashes, chat transcripts, or the repository that produced them.

## What PASS can do

- **Author durable knowledge.** Convert studied instruction into Patterns
  (reusable decisions), APs (ordered action procedures), and Drills (deliberate
  practice with feedback and stopping criteria).
- **Support autonomous and taught authoring.** Source-sufficient domains can be
  authored autonomously; interpretation-heavy domains can incorporate formal
  human teaching and correction before knowledge becomes canonical.
- **Keep domains independent.** Each domain owns its cards and may depend only
  on itself plus the universal `metaskills` baseline.
- **Retrieve a small working set.** Rank relevant cards for a task without
  loading a whole domain or maintaining a global registry.
- **Separate learned principles from observed results.** Skillset Memory keeps
  durable transferable lessons distinct from empirical training outcomes;
  `training_history.jsonl` preserves their event-level evidence. Neither replaces
  canonical cards.
- **Validate the library.** Check card schemas, IDs, relationships,
  prerequisites, assets, visual references, generated indexes, memory, and
  release portability.
- **Read bounded PDF units.** Extract selected PDF pages as disposable text and
  flag pages that still need visual inspection or OCR.
- **Create project workspaces.** Build a pruned domain-specific folder for local
  work or a ZIP for a Project/chat environment, optionally with extracted source
  text, tests, and canonical release recipes.
- **Import a returned project archive safely.** Preview, validate, and then add
  or update approved files without blindly unpacking over the repository.
- **Build self-contained skill releases.** Resolve `metaskills` and the complete
  prerequisite closure, then enforce schema, asset, reference, and portability
  gates before packaging.
- **Guide productive work at runtime.** Released domain skills route tasks to
  applicable APs, Patterns, variants, teaching lanes, execution modes, and risk
  checks while leaving native judgment responsible for the actual work.

The current full repository contains Art, Game Design, Software Engineering,
and Writing. These are discovered from `library/`; the architecture is not
hardcoded to those four domains.

## The five things people often confuse

| Artifact | Purpose | Durable? | Ships in a skill release? |
| --- | --- | --- | --- |
| Source material | Evidence used while learning | No PASS dependency | No |
| Card | Canonical reusable knowledge | Yes | Yes, when selected |
| Skillset Memory | Evidence about real attempts | Yes, but not canon | Yes, for a selected domain |
| Project snapshot | A bounded PASS workspace for a Python-capable chat LLM | Temporary/workable | No |
| Release | A self-contained skill product | Yes | It is the product |

**PASS is the factory. [SkillForge](https://github.com/Methuselas/The_Skill_Forge) is
the distribution repository for finished skillsets.** Project snapshots are
working copies of part of the factory; releases are the portable products made
by it.

## Repository map

- `PASS/` — portable authoring method, contracts, templates, runtime, and tools
- `library/` — canonical cards organized into independent domain packages
- `library/metaskills/` — universal process knowledge included in every release
- `memory/` — per-domain learned and calibrated state plus empirical training history, separate from canon
- `docs/` — human-facing repository and skill-author guides
- `workspace/tools/` — PDF extraction and project snapshot utilities
- `workspace/release-recipes/` — named release products; canonical recipes start
  with `SkillForge_`
- `workspace/handoffs/` — domain-prefixed project continuity and trainer-entry
  documents; included only with matching project domains, never in releases
- `tests/` — architecture, runtime, tool, and release checks
- `.agents/skills/`, `.claude/skills/` — repository discovery wrappers; these do
  not become release dependencies
- `archive/` — retired material; active files may not depend on it

## Quick start

PASS tools require Python. PyYAML is the only package dependency.

```bash
python -m pip install -r PASS/requirements.txt
python PASS/tools/validate.py
python PASS/tools/verify_references.py
python PASS/tools/build_index.py --check
python PASS/tools/memory.py validate
python -m unittest discover -s tests -p "test_*.py"
```

Validate one domain while maintaining it:

```bash
python PASS/tools/validate.py --package art
```

Retrieve a bounded set of relevant knowledge instead of opening a whole index:

```bash
python PASS/tools/find_relevant.py --package metaskills --cues "plan verify revise" --limit 5
python PASS/tools/find_relevant.py --package art --cues "foreshortened hand gripping" --limit 8
```

## Run PASS inside a Python-capable chat

A **project snapshot** is an uploadable working environment made specifically
for a chat LLM that can unpack files, read and write a project directory,
execute Python, and return a ZIP. It lets that LLM perform real PASS authoring
runs inside the chat window without cloning this repository, using Git, or
accessing the maintainer's machine.

A project snapshot is not an installable skill and is not published through
SkillForge. It is a temporary copy of the part of the PASS factory needed to
study sources, create or revise cards, update Skillset Memory when appropriate,
regenerate indexes, and run the actual validators. The returned work is reviewed
and imported into the canonical PASS repository; a SkillForge release can be
built later from accepted work.

The project builder automatically includes:

- the portable `PASS/` authoring skill, documentation, templates, and tools;
- `library/metaskills/` and the selected domain library;
- the selected domain's Skillset Memory;
- matching host-discovery skills and root instructions;
- reusable utilities from `workspace/tools/`; and
- domain-prefixed project handoffs and canonical release recipes; and
- optional tests and bounded text source inputs when requested.

It deliberately leaves out unrelated domains, `.git`, retired archives, source
PDFs, nested ZIPs, release outputs, caches, and workspace scratch. The result is
small enough to hand to a chat while remaining capable of validating its own
PASS work.

### The project-snapshot round trip

1. Build a domain-scoped project ZIP locally.
2. Upload it to a chat or Project environment that provides file access and
   Python execution. Attach the source separately, or include a bounded `.txt`
   or `.md` extract under `SOURCE_INPUT/` as shown below.
3. Tell the LLM to unpack the archive, work inside its single
   `PASS-project-*` root, begin with `AGENTS.md` and `PASS/SKILL.md`, and perform
   one domain-scoped PASS run.
4. The LLM edits the project files, regenerates indexes, runs the bundled PASS
   validators, and returns an updated ZIP preserving the same single root.
5. Back in the canonical repository, preview the returned archive with the
   importer. Apply it only after the proposed changes pass review.

A suitable instruction to the chat is:

> Unpack this PASS project snapshot and work only inside its `PASS-project-*`
> root. Read `AGENTS.md` and `PASS/SKILL.md`, then perform one PASS authoring run
> for the selected domain using the supplied source. Regenerate indexes, run the
> bundled validation tools, and return the updated project as a ZIP with the
> original single root preserved.

Python accelerates and verifies the run; it does not replace the PASS authoring
method. The host also needs permission to read and write uploaded files. A chat
that cannot execute Python or return files can discuss PASS, but it cannot use a
project snapshot for the intended validated round trip.

### Build a project snapshot

Create a new local project folder:

```bash
python workspace/tools/build_project_snapshot.py workspace/projects/PASS-project-art --domain art
```

Create the equivalent uploadable ZIP:

```bash
python workspace/tools/build_project_snapshot.py workspace/releases/PASS-project-art.zip --domain art
```

Inside the unpacked chat project, install the one runtime dependency if the host
does not already provide it:

```bash
python -m pip install -r PASS/requirements.txt
```

Before returning the project, regenerate navigation and run the bundled checks:

```bash
python PASS/tools/build_index.py
python PASS/tools/validate.py --package art
python PASS/tools/verify_references.py
python PASS/tools/memory.py validate
```

Add a bounded source extract at the visible top-level `SOURCE_INPUT/` folder:

```bash
python workspace/tools/extract_pdf_text.py book.pdf workspace/authoring/book-unit.txt --pages 20-48
python workspace/tools/build_project_snapshot.py workspace/releases/PASS-project-writing.zip --domain writing --source-text workspace/authoring/book-unit.txt
```

Useful options:

- Repeat `--domain` to create a multi-domain project.
- Add `--include-tests` when the project will maintain repository code.
- Add `--exclude-recipes` only when a deliberately reduced project should omit
  canonical `SkillForge_*.yaml` recipes.
- Add `--force` to replace an existing ZIP. Existing project directories are
  never replaced; choose a new folder name so no working copy is destroyed.

A source passed with `--source-text` is copied into the project only; it is never
added to this repository automatically. Source material remains evidence for the
run and is never a dependency of a finished card.

## Import an updated project archive

Export the updated project as a ZIP that preserves its single
`PASS-project-*` root, then run the importer once without `--apply`:

```bash
python workspace/tools/import_project_snapshot.py path/to/PASS-project-art.zip
```

That is a dry run. It inspects the ZIP boundary, validates the archived cards,
visual references, generated indexes, and memory with the repository's trusted
tools, then prints every proposed addition or update.

If the plan is correct, apply it:

```bash
python workspace/tools/import_project_snapshot.py path/to/PASS-project-art.zip --apply
```

By default, only `library/<domain>/`, `memory/<domain>/`, domain-prefixed
`workspace/handoffs/*.md` files, and the selected domain's canonical recipe are
eligible. If the project intentionally changed shared PASS documentation, tools,
tests, matching host skills, `metaskills`, or other domains' canonical recipes,
preview that larger scope and then apply it explicitly:

```bash
python workspace/tools/import_project_snapshot.py path/to/PASS-project-art.zip --all-project-files
python workspace/tools/import_project_snapshot.py path/to/PASS-project-art.zip --all-project-files --apply
```

The importer never imports `SOURCE_INPUT`, unrelated domains or their handoffs,
or legacy recipes, and never deletes a repository file because it is absent from
the archive. It rejects traversal paths, links, duplicate/case-colliding names,
unknown domains, oversized payloads, invalid cards, broken references, stale
indexes, and invalid memory before writing. Each changed file is replaced
atomically, with rollback copies prepared for the complete plan.

If a project adds or changes cards, regenerate its indexes before exporting the
return archive:

```bash
python PASS/tools/build_index.py
```

A deliberate removal or rename needs a separate reviewed repository edit. The
importer cannot safely infer deletion merely from absence in an archive.

## Author knowledge from a source

Read [the PASS user guide](docs/PASS_USER_GUIDE.md) for the human workflow and
[`PASS/docs/PASS_RUN.md`](PASS/docs/PASS_RUN.md) for the complete authoring
procedure. In compact form:

1. Determine the source's actual instructional subject.
2. Divide it into coherent units defined by instruction—not page count or chat
   length.
3. Read one unit deeply before naming cards.
4. Resolve genuine ambiguity with a teacher when the domain requires it.
5. Re-read the same unit and extract only durable, reusable knowledge.
6. Place each candidate as a new card, variant, replacement, or rejection inside
   one domain.
7. Regenerate indexes, validate, and present the canonical delta.

The object contracts are closed. Never widen the schema to accommodate a card,
and never put source provenance or practice history into canon. See
[`PASS/docs/PASS_SCHEMA.md`](PASS/docs/PASS_SCHEMA.md) and
[`PASS/docs/PASS_DOCTRINE.md`](PASS/docs/PASS_DOCTRINE.md).

## Testing software cards against real code

Software card field tests apply one card to one bounded slice of human-written
software, build a small proof of concept, and compare engineering decisions.
They are distinct from Drills and comparative treatment/control studies. See
[`PASS/docs/SOFTWARE_CARD_FIELD_TESTS.md`](PASS/docs/SOFTWARE_CARD_FIELD_TESTS.md).

Each review records why its subject was chosen: from a neutral external pool,
for relevance to an active project, or from personal interest. These are all
useful field evidence, but they support different claims. PASS ships a blank
local-context template rather than embedding any maintainer's source choices in
the public protocol.

The template is maintained by the model, not filled out by the user. Code plus a
plain-language goal is enough to start. A catalog is optional and is needed only
when the user wants the model to select a neutral external project; the user can
paste a link, name a preferred list, or ask the model to offer one.

The full protocol is for maintainers qualifying cards. Ordinary users can simply
ask PASS to review, fix, or build their software; they are not required to run a
study first. Qualification begins with the authored language module. Evidence
that a core card works in one language supports that language only, and finding a
real defect in the human code is useful evidence rather than a failed review.

Verified coverage does not determine ownership. A cross-language decision lives
in one shared core even if it was learned from a C++ book or has only been tested
in C++ so far. Language modules contain the language's realization, idioms,
constraints, and exceptions. Releases ship that shared core once rather than
duplicating a private core folder for every language.

## What Drills are for

Patterns hold reusable decisions, APs coordinate those decisions into complete
actions, and **Drills build or test the capability to apply them**. A Drill is
not another explanation card and it is not decorative homework. It creates a
repeatable attempt with a defined task, setup, required output, success check,
and plausible failure modes.

### Training and evaluating AI today

PASS currently uses Drills primarily for deliberate AI practice and capability
evaluation. A Drill can strengthen a weak behavior, test whether a skill
transfers to a fresh problem, or expose a failure that fluent prose would hide.
The taker must produce the requested artifact, action, or observation—describing
what would happen is not a completed attempt.

For a meaningful evaluation, administer the Drill blind. Hide either the
Instructions or the Success Check, depending on whether the sitting measures
unprompted capability or execution after instruction. Freeze the produced answer
before revealing the grading criteria, and use a separate grader when possible.
Several Drills may share one artifact when the goal is to expose interactions
between capabilities rather than score one in isolation.

Results from real attempts belong in Skillset Memory. They do not automatically
rewrite a Drill, Pattern, or AP, and an invalid run never counts as evidence of a
craft weakness.

### Software-engineering Drills

Software Drills distinguish portability probes, blind sittings, deterministic
regressions, and comparative studies before work begins. Most use one taker and
an independent compiler or test runner; only an explicitly approved comparative
study receives a treatment/control pair. A negative case is required when the
claimed capability is enforcement, because a successful build alone does not
show that misuse is caught.

Assertion, guard, comment, attribute, file, and line counts are diagnostics, not
quality verdicts. Suspected contamination pauses a batch; confirmed contamination
terminates its active and queued arms without an automatic retry. The exact
packet separation, evidence rules, and sub-agent ceilings are in
[`PASS/docs/PASS_CONSUMPTION.md`](PASS/docs/PASS_CONSUMPTION.md#software-engineering-drill-runs).
Repository maintainers can generate the current inventory with
[`PASS/tools/drill_inventory.py`](PASS/tools/drill_inventory.py) and inspect the
small C++ administration pilot under
[`tests/fixtures/software_engineering_drills/`](tests/fixtures/software_engineering_drills/).

For an actual blind sitting, the optional
[`PASS/runtime/skillforge_drill.py`](PASS/runtime/skillforge_drill.py) helper
implements the shared prepare → produce → freeze → reveal → grade → finalize
lifecycle. It is model-neutral: it standardizes evidence boundaries and stopping
rules, not the taker's reasoning style. Only `student/` is exposed before freeze;
`controller/` stays private, every canonical Success Check bullet must receive a
grader disposition, and finalization exports a candidate history event without
editing Skillset Memory. Releases that contain Drill cards receive the same
helper automatically under `scripts/skillforge_drill.py`. See
[`PASS/docs/PASS_CONSUMPTION.md`](PASS/docs/PASS_CONSUMPTION.md#optional-model-neutral-drill-runner)
for the command sequence.

### Teaching humans with AI later

Drills are also the foundation for a future mode in which an AI teaches a human
through guided practice. In that mode the AI would select an appropriate Drill,
present the task without leaking its answer, observe the learner's actual work,
apply the Success Check, explain the relevant failure, and choose a next attempt
or prerequisite.

The present Drill schema already separates practice, instruction, assessment,
and common failures, but PASS does not yet claim a complete human-teaching
system. Human-facing pacing, hint policy, accessibility, safety, progression,
and evidence of learning still need to be designed and tested before that mode
is declared mature. See
[`PASS/docs/PASS_CONSUMPTION.md`](PASS/docs/PASS_CONSUMPTION.md) for current
administration rules and [`PASS/docs/PASS_SCHEMA.md`](PASS/docs/PASS_SCHEMA.md)
for the closed Drill contract.

## Use Skillset Memory

Skill Memory keeps durable learned principles separate from empirical training
results; `training_history.jsonl` records the underlying attempts and
evaluations. None of these rewrite canonical knowledge automatically.

```bash
python PASS/tools/memory.py query --domain art --cues "hand,grip" --limit 5
python PASS/tools/memory.py append --domain art --task "Draw a gripping hand" --note "..."
python PASS/tools/memory.py review --domain art
python PASS/tools/memory.py validate
```

Invalid runs are recorded as tool, controller, package, or interface failures;
they never count as evidence of a craft weakness. The full contract is in
[`PASS/docs/MEMORY_SCHEMA.md`](PASS/docs/MEMORY_SCHEMA.md).

## Build an installable release

Named releases select a product intent. PASS resolves the complete dependency
closure, always adds `metaskills`, materializes the release, and validates the
files that actually ship.

The builder does not contain a machine-specific destination. The recipe and
output paths are arguments supplied by whoever runs it:

```bash
python PASS/tools/build_release.py build <recipe> <release-directory> --zip <distribution-zip>
python PASS/tools/build_release.py check <release-directory>
```

Both outputs must be outside the PASS checkout. The release directory is the
validated, unpacked product; the optional ZIP is the same product prepared for
upload or distribution. Existing destinations are never replaced unless the
maintainer deliberately adds `--replace` after checking the paths.

### Publishing PASS releases to SkillForge

The intended maintainer layout is two independent checkouts plus any external
build directory:

```text
<workspace>/
├── PASS/
├── SkillForge/
│   └── releases/
└── release-builds/
```

With that layout, a build from the PASS checkout can write its validated working
directory to `<workspace>/release-builds/` and its distributable ZIP directly to
the sibling SkillForge checkout. For example:

```bash
python PASS/tools/build_release.py build workspace/release-recipes/SkillForge_Art.yaml ../release-builds/SkillForge_Art --zip ../SkillForge/releases/SkillForge-Art.zip
python PASS/tools/build_release.py check ../release-builds/SkillForge_Art
```

The same relationship works wherever the repositories were cloned. On one
Windows machine `<workspace>` might be `D:\Repos`; on another machine it could
be `C:\work`, `/home/alex/code`, or any other location. No absolute path is
written into the release, and consumers do not need either repository after
downloading the ZIP.

The four canonical PASS recipes map to SkillForge distribution files as follows:

| PASS recipe | SkillForge release |
| --- | --- |
| `SkillForge_Art.yaml` | `SkillForge/releases/SkillForge-Art.zip` |
| `SkillForge_Game_Design.yaml` | `SkillForge/releases/SkillForge-Game-Design.zip` |
| `SkillForge_Software_Engineering.yaml` | `SkillForge/releases/SkillForge-Software-Engineering.zip` |
| `SkillForge_Writing.yaml` | `SkillForge/releases/SkillForge-Writing.zip` |

Every result is self-contained: it needs no source material, PASS checkout,
SkillForge checkout, Git history, authoring memory, or external card path at
runtime. The published packages are available from the
[SkillForge repository](https://github.com/Methuselas/The_Skill_Forge). See
[`PASS/docs/MODULE_RELEASES.md`](PASS/docs/MODULE_RELEASES.md) and
[`PASS/docs/RELEASE_INSTALL.md`](PASS/docs/RELEASE_INSTALL.md).

## Add a domain

Create `library/<domain>/` plus matching discovery skills under
`.agents/skills/` and `.claude/skills/`. Optional empirical history belongs in
`memory/<domain>/`. Keep authoring in one domain per run, use only that domain
plus `metaskills`, and let discovery tools find the new package automatically.

Do not add a global registry, repo-wide hand-authored index, new root-level tool,
or cross-domain card dependency. Detailed module and release guidance is in
[`docs/SKILL_AUTHOR_GUIDE.md`](docs/SKILL_AUTHOR_GUIDE.md).

## Versioning and beta status

PASS follows [Semantic Versioning 2.0.0](https://semver.org/). The current
version is recorded in [`VERSION`](VERSION), and generated SkillForge manifests
record it as `pass_version`.

The PASS public compatibility surface is the documented card and module schema,
runtime and memory contracts, command-line interfaces, project snapshot/import
boundary, release recipe format, and release manifest. Version changes mean:

- **MAJOR** — an incompatible change to that public compatibility surface;
- **MINOR** — backward-compatible functionality or an explicitly optional
  extension; and
- **PATCH** — a backward-compatible correction that adds no public capability.

`1.0.0-beta.1` was the first formal public beta of the intended `1.0.0`
contract; the current version is `1.0.0-beta.5`. Beta builds increment the
prerelease number and may contain clearly documented corrections that are
incompatible with an earlier beta. Stable `1.0.0` means the public surface is
defined and future incompatible changes require a new major version.

This is the version of the PASS factory, not a claim that every knowledge domain
changes in lockstep. SkillForge skillsets may eventually carry their own product
versions; `pass_version` records which factory contract produced a release. Once
a version is published, its contents are never silently replaced. Changes receive
a new version and an entry in [`CHANGELOG.md`](CHANGELOG.md).

## Contributing

Contributions are welcome, including corrections, additional knowledge, tooling
improvements, and independent new skillsets. Start with
[`CONTRIBUTING.md`](CONTRIBUTING.md), which explains domain boundaries,
validation, release expectations, and how contributed work remains open.

## License and project identity

PASS uses split open, share-alike licensing:

- executable tools and runtime code are licensed under
  `AGPL-3.0-or-later`; and
- knowledge cards, Agent Skill instructions, documentation, declarative
  profiles, recipes, and original assets are licensed under `CC-BY-SA-4.0`.

This permits personal, educational, community, and commercial use while
requiring covered redistributions and adaptations to preserve attribution and
the applicable open terms. The official releases remain freely available from
[SkillForge](https://github.com/Methuselas/The_Skill_Forge).

See [`LICENSE.md`](LICENSE.md) for scope, [`NOTICE.md`](NOTICE.md) for required
attribution, and [`TRADEMARKS.md`](TRADEMARKS.md) for use of the PASS and
SkillForge names.

## Acknowledgments

PASS builds on the Agent Skills format introduced and openly documented by
Anthropic. Anthropic's published skills and specification established the
portable `SKILL.md` convention that made this project possible. PASS and
SkillForge are independent community projects and are not affiliated with or
endorsed by Anthropic.

- [Anthropic Agent Skills](https://github.com/anthropics/skills)
- [Agent Skills specification](https://agentskills.io)

## Support PASS

If PASS or a SkillForge release helps you, the best ways to support the project
are to star and share [PASS](https://github.com/Methuselas/PASS), share the free
[SkillForge releases](https://github.com/Methuselas/The_Skill_Forge), report concrete
problems, improve an existing skillset, or contribute a new one. If you would
also like to support its continued development financially, you can
[buy Methuselas a coffee](https://buymeacoffee.com/methuselas). Supporting the
project never changes the licensing or access to PASS or its SkillForge
releases.

## Non-negotiable boundaries

- Cards survive their sources.
- Domains do not depend on other domains.
- Indexes are generated, never hand-edited.
- Skillset Memory separates learned principles from empirical results and is never canon.
- `archive/` is retired and cannot support active behavior.
- `.agents/` and `.claude/` are discovery only, never release dependencies.
- Every release includes `metaskills` and the full prerequisite closure.
- Project snapshots are workspaces; release ZIPs are products.

For repository agents, `AGENTS.md` and `CLAUDE.md` are the authoritative routing
and safety entrypoints.
