---
name: pass-authoring
description: >-
  Use when studying sources or maintaining PASS APs, Patterns, Drills, modules,
  variants, references, prerequisites, release recipes, validation, or skill
  packaging in this PASS repository.
---

# PASS Authoring

Use the canonical portable PASS package in `PASS/`; this repo skill is only a
discovery wrapper for agents working inside PASS.

## References by phase

Do not preload the complete PASS documentation set. Read `PASS/SKILL.md` when a
PASS authoring or maintenance operation begins, then open only what the current
phase needs:

- purpose, admissibility, or extraction judgment: the relevant section of
  `PASS/docs/PASS_DOCTRINE.md`;
- preflight, source reading, reconciliation, third read, or closure: the relevant
  section of `PASS/docs/PASS_RUN.md`;
- card creation or review: frontmatter rules plus the applicable Pattern, Drill,
  or AP section of `PASS/docs/PASS_SCHEMA.md`;
- placement or module ownership: `PASS/docs/PASS_LIBRARY.md`;
- project archives, skill-release destinations, packaging or dependency changes:
  `PASS/docs/MODULE_RELEASES.md` (see §Maintainer destinations), adding
  `PASS/docs/EXECUTION_CONTRACT.md` only for runtime routing or completion work;
- drill administration or domain consumption: `PASS/docs/PASS_CONSUMPTION.md`;
- memory work: `PASS/docs/MEMORY_SCHEMA.md`.

Read a complete document only when the task genuinely spans its complete
contract. A later phase may load another reference; future need is not a reason
to load it now.

## Rules that decide most questions here

Ordinary source study first runs `python PASS/pass.py resume --domain
<authorized-domain> --source <source>`: an unfinished run of that source is
continued, never duplicated. Only when it reports none, run `python PASS/pass.py
start --source <source> --domain <authorized-domain>`. Follow the executable
phases. After LOAD, deterministic Source Prep creates or verifies the reusable
model-facing package before one source-wide preflight. User requests such as
"prep this for PASS" map to `--stop-after source_prep`; "run through preflight"
or "stop before ingesting units" map to `--stop-after preflight`. If `resume`
requires `recover`, restore the last verified hard checkpoint before doing any
new work. Keep provisional cards in
`Pass-runs/<domain>[/<module-path>...]/<run-id>/drafts/<category>/`. `Pass-runs/`
is the one run root; a run is filed at the library ownership path its cards land
in (`--owner languages/python`), and its directory is a short opaque id such as
`r_a1b2c3d4`. Source titles are recorded as run metadata, never as a path
segment. A valid
source-wide preflight stops at its presentation/acceptance gate: run `present`,
show the complete packet, and wait for explicit user confirmation before
`accept-preflight` releases PASS 1. If the user explicitly authorizes this one
source to continue unattended, record it with `python PASS/source.py authorize ...`,
then loop on `source.py drive` and execute only the action it returns; claim
progress only from `source.py report`. It never answers a practitioner checkpoint
or consumes an `approval_required` delta. Read
`PASS/docs/AUTHORING_RUNTIME.md` for commands and recovery alongside the human
rules in `PASS/docs/PASS_RUN.md`. The old preflight helper alone cannot authorize
ingestion. Repository maintenance and packaging do not need a source run. Existing Unreal Niagara assets use the separate `python PASS/vfx.py` analysis lane rather than source preflight; read `PASS/docs/UNREAL_VFX_PASS.md` before such a run.

Stage responses use the closed Stage Contract v1 envelope,
`{"action_id": ..., "payload": ...}`: run `template` for the pending stage, fill
only the payload, and submit it. Return drafted cards as structured objects with
`object_id`, `object_type`, `library_path`, `name`, frontmatter and the
object-type body; the host derives every filename and path and renders the
Markdown, so never name a file or compose a path. Never restate `unit_id`,
`schema_version`, a stage name, a digest map or a mode -- the host owns them and
will refuse them. A malformed response gets one structured correction attempt and
then fails closed. `python PASS/pass.py schema --stage <stage>` is authoritative;
see `PASS/docs/STAGE_CONTRACT.md`.

`library/` holds finished knowledge. Active, per-source transactional state lives
only in `Pass-runs/` and may travel in a continuation project
snapshot; it is not a ledger, source registry, provenance record, Skillset Memory
entry, or finished-skill dependency. Unit deltas remain staged until source close.

A card must be valid and executable after its source is gone. Never write a
`source_id`, locator, page number, or hash onto a card. `reference` is optional
attribution (title and author) and nothing reads it.

Author in one domain per run. Duplicate-guard against that domain only. Cards may
reference their own domain plus `metaskills`; any other cross-package reference
fails validation.

A run has three reads, not two. The third is of the cards the run produced, read
cold against the schema before the delta is presented (`PASS/docs/PASS_RUN.md`
§2.6). `validate.py` is its floor, not its substance: the defects that have forced
lane-wide repair sweeps all passed the validator on the day they were written.

Do not make released skills depend on this repo, `.agents/`, or `.claude/`.
Nothing may depend on `archive/`.

Art may require a human-guided chapter discussion before commit. Software
Engineering may be authored autonomously when the source and task support it.
Never invent questions as ceremony, but stop for real ambiguity, contradiction,
or teacher-dependent interpretation.

## Skillset Memory

`memory/<domain>/` is a separate store with its own contract in
`PASS/docs/MEMORY_SCHEMA.md`. Read that before touching it.

Skill Memory separates what testing showed (`training_result`) from the durable
lesson retained from evidence (`learned_principle`). Training history keeps the
event trail. Memory is never canon and never overrides a card — an entry that seems important
enough to apply on every turn has earned promotion review, not a paste, because
pasting creates a second write site and lets the real owner decay unobserved.
`tests/test_memory.py` enforces this.

When a domain gains, removes, or renames a module, update that domain's canonical
`SkillForge_*.yaml` recipe in the same change. When an approved cross-skill
category is selected as an auxiliary, update the consuming recipe's bounded
auxiliary entries in the same change. A project archive must not be the only
place where its release composition is correct.

An observation is evidence about a capability only if the run that produced it
was a valid test of that capability. A run that failed before the capability was
exercised stays in `training_history.jsonl` and never counts toward a craft
weakness; attribute it to the tool, controller, or package that actually failed.

```bash
python PASS/tools/memory.py validate
python PASS/tools/memory.py review --domain <domain>
python PASS/tools/memory.py compact --domain <domain>
python PASS/tools/memory.py add|update|retire|show --domain <domain> ...
```

Change memory only through those commands; each validates the whole store before
an atomic write, so never hand-edit `skill_memory.yaml`. `add` generates the
claim's id — a caller never supplies one, and a retired id is never reissued.
Retirement is removal: `retire` requires `--reason`, which is operator-facing at
the moment of the write and is persisted nowhere. There is no `supersede`; a
replacement is `retire` then `add`, with a fresh id and an independently
re-derived `confidence`, because no tool may compute, suggest, or copy one.

The card tools read `library/` and the memory tool reads `memory/`. Keep them
apart; neither store is an input to the other.

Before publishing changed knowledge, run the tools under `PASS/tools/`:

```bash
python PASS/tools/validate.py
python PASS/tools/verify_references.py
python PASS/tools/build_index.py
```

Release building must not bypass the quality gates.
