# PASS — Durable skillsets built from studied knowledge

PASS (Pattern Analysis Skill System) is an authoring, validation, and packaging
system for AI skills. It turns books, courses, documents, code, visual material,
and formal human teaching into small, reusable knowledge cards that still work
after the original source is gone.

PASS is not a document search system and it is not a folder of prompts. It is a
factory for building skillsets with explicit decisions, procedures, practice,
dependencies, runtime routing, validation, memory, project workspaces, and
self-contained releases.

Finished, installable skillsets are published separately in
[SkillForge](https://github.com/Methuselas/SkillForge). PASS is the authoring
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
- **Record empirical skill history.** Skillset Memory stores what happened in
  valid attempts without copying practice history into canonical cards.
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
| Skillset Memory | Evidence about real attempts | Yes, but not canon | No |
| Project snapshot | A bounded authoring workspace | Temporary/workable | No |
| Release | A self-contained skill product | Yes | It is the product |

**PASS is the factory. [SkillForge](https://github.com/Methuselas/SkillForge) is
the distribution repository for finished skillsets.** Project snapshots are
working copies of part of the factory; releases are the portable products made
by it.

## Repository map

- `PASS/` — portable authoring method, contracts, templates, runtime, and tools
- `library/` — canonical cards organized into independent domain packages
- `library/metaskills/` — universal process knowledge included in every release
- `memory/` — per-domain empirical history, separate from canon
- `docs/` — human-facing repository and skill-author guides
- `workspace/tools/` — PDF extraction and project snapshot utilities
- `workspace/release-recipes/` — named release products; canonical recipes start
  with `SkillForge_`
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

## Create a project folder or archive

The project builder automatically includes PASS, `metaskills`, the selected
domain, its memory, matching host skills, the root documentation, and every
reusable script in `workspace/tools/`.

Create a new local project folder:

```bash
python workspace/tools/build_project_snapshot.py workspace/projects/PASS-project-art --domain art
```

Create the equivalent uploadable ZIP:

```bash
python workspace/tools/build_project_snapshot.py workspace/releases/PASS-project-art.zip --domain art
```

Add a bounded source extract at the visible top-level `SOURCE_INPUT/` folder:

```bash
python workspace/tools/extract_pdf_text.py book.pdf workspace/authoring/book-unit.txt --pages 20-48
python workspace/tools/build_project_snapshot.py workspace/releases/PASS-project-writing.zip --domain writing --source-text workspace/authoring/book-unit.txt
```

Useful options:

- Repeat `--domain` to create a multi-domain project.
- Add `--include-tests` when the project will maintain repository code.
- Add `--include-recipes` to include only canonical
  `SkillForge_*.yaml` recipes.
- Add `--force` to replace an existing ZIP. Existing project directories are
  never replaced; choose a new folder name so no working copy is destroyed.

Snapshots deliberately exclude `.git`, retired archives, source PDFs, nested
ZIPs, unrelated domains, release outputs, caches, and workspace scratch. A
source passed with `--source-text` is copied into the project only; it is never
added to this repository automatically.

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

By default, only `library/<domain>/` and `memory/<domain>/` are eligible. If the
project intentionally changed shared PASS documentation, tools, tests, matching
host skills, `metaskills`, or canonical recipes, preview that larger scope and
then apply it explicitly:

```bash
python workspace/tools/import_project_snapshot.py path/to/PASS-project-art.zip --all-project-files
python workspace/tools/import_project_snapshot.py path/to/PASS-project-art.zip --all-project-files --apply
```

The importer never imports `SOURCE_INPUT`, never imports unrelated domains or
legacy recipes, and never deletes a repository file because it is absent from
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

## Use Skillset Memory

Memory records evidence from actual attempts; it does not rewrite canonical
knowledge automatically.

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
[SkillForge repository](https://github.com/Methuselas/SkillForge). See
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
[SkillForge](https://github.com/Methuselas/SkillForge).

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
[SkillForge releases](https://github.com/Methuselas/SkillForge), report concrete
problems, improve an existing skillset, or contribute a new one. If you would
also like to support its continued development financially, you can
[buy Methuselas a coffee](https://buymeacoffee.com/methuselas). Supporting the
project never changes the licensing or access to PASS or its SkillForge
releases.

## Non-negotiable boundaries

- Cards survive their sources.
- Domains do not depend on other domains.
- Indexes are generated, never hand-edited.
- Skillset Memory is empirical state, never canon.
- `archive/` is retired and cannot support active behavior.
- `.agents/` and `.claude/` are discovery only, never release dependencies.
- Every release includes `metaskills` and the full prerequisite closure.
- Project snapshots are workspaces; release ZIPs are products.

For repository agents, `AGENTS.md` and `CLAUDE.md` are the authoritative routing
and safety entrypoints.
