---
name: pass-authoring
description: >-
  Use when studying a source to extract, review, validate, organize, revise, or
  publish PASS APs, Patterns, Drills, modules, or portable releases. Also use for
  PASS schema and library maintenance work. Human-guided teaching may be required
  when source material alone is insufficient.
---

# PASS Authoring

This skill governs creation and maintenance of PASS knowledge objects. It is
separate from the domain skills that consume those objects.

A finished card is the durable artifact. It must be valid and executable after
the source it was learned from is gone, so it carries no source id, locator,
page, hash, or receipt.

## Canonical references by phase

Do not preload every PASS document. Open the reference that owns the current
decision:

- purpose, admissibility, and extraction judgment: the relevant section of
  `docs/PASS_DOCTRINE.md`;
- preflight, source reading, reconciliation, third read, and closure: the
  relevant section of `docs/PASS_RUN.md`;
- object creation or review: the frontmatter contract and applicable Pattern,
  Drill, or AP section of `docs/PASS_SCHEMA.md`;
- placement and module ownership: `docs/PASS_LIBRARY.md`;
- project archives, skill-release destinations, packaging, and dependencies:
  `docs/MODULE_RELEASES.md` (see §Maintainer destinations);
- runtime profile routing, vendoring, or completion contracts:
  `docs/EXECUTION_CONTRACT.md`;
- skill consumption or drill administration: `docs/PASS_CONSUMPTION.md`;
- software card field tests against human-written code:
  `docs/SOFTWARE_CARD_FIELD_TESTS.md`;
- Skillset Memory: `docs/MEMORY_SCHEMA.md`.

Read a complete document only when the task genuinely spans its complete
contract. Load later-phase references when that phase begins, not in anticipation.

## Working rules

For ordinary source authoring, start with `python PASS/pass.py start --source
<source> --domain <authorized-domain>` from the project root. Follow its current
phase through LOAD, the **one source-wide preflight**, its mandatory presentation
and explicit user-acceptance gate, then one unit's PASS 1 / 2 / 3 and verified
landing. **Preflight never repeats per unit.** A validated preflight does not
release PASS 1: run `present`, reproduce the complete preflight packet, and wait
for explicit user confirmation of the stated subject and provisional source-wide
plan before `accept-preflight`. Do not treat the original request to run PASS as
that confirmation. After the source plan is accepted, the next unit begins at
PASS 1; `replan` may amend remaining instructional boundaries before that unit's
PASS 1 is accepted, but it is not a new preflight and does not authorize another
structural read. Read
`docs/PASS_RUN.md` for the human rules and `docs/AUTHORING_RUNTIME.md` for
commands, records and recovery. The standalone preflight helper and reading
the Markdown alone do not start an authorized executable run. Maintenance and
release packaging do not need a source run.

When the user explicitly authorizes one source to continue unattended through
completion, finish LOAD first, then record that bounded instruction with `python PASS/source.py
authorize --run <run-directory> --reason <user-instruction>`. The source runner does not fabricate PASS reads: the host still performs the substantive reading and adjudication, but in unattended mode it must obtain the next action from `python PASS/source.py drive --run <run-directory>` before every preflight/PASS/checkpoint submission. `PASS/pass.py` rejects unattended substantive submissions that lack the matching persisted action lease. The runner also consumes routine presentation/acceptance and landing gates after rendering their complete packets into the run audit. Progress claims must come from `python PASS/source.py report --run <run-directory>`, never from model narration or memory. It must stop for practitioner-dependent checkpoint
answers, any `approval_required` delta, source-identity failure, or unrecoverable
controller error. See `docs/AUTHORING_RUNTIME.md` §Unattended single-source mode.

At `land`, run `python PASS/pass.py present --run <run-directory>` and reproduce
the complete generated landing packet **without summarizing, regrouping, or
omitting empty buckets/reasons** before recording a landing decision. The
controller binds the decision to that packet's SHA-256 and leaves approval basis
blank until the actual approval/evidence gate is satisfied.

Use the source material named by the user as the evidentiary basis. Preserve its
terminology and scope. Do not silently fill unsupported gaps with general
knowledge. Mark inference, uncertainty, and deferred review explicitly.

Author in **one** domain per run. Duplicate-guard against that domain only; do not
search or modify another. Cards may reference their own domain plus `metaskills`.

When using the repository workspace, follow `docs/PASS_RUN.md` §Workspace
lifecycle: choose an existing purpose bucket and task directory, then remove
owned scratch after verified integration/completion, respecting evidence holds.

Treat AP authoring as **orchestration authoring**, not merely another extraction
shape. A source may teach an AP directly, but a stable AP may also be synthesized
from accepted Patterns when a recurring action needs dependable ordering, gates,
recovery, and completion. See `docs/PASS_RUN.md` §2.8. During execution, productive
actions resolve AP-first; Pattern-first assembly is the fallback when coverage is
missing.

Every run ends with a **third read**: the cards it just produced, read cold
against the schema, before the delta is presented. See `docs/PASS_RUN.md` §2.6.
The validator is the floor of that pass, not the pass — a Success Check nothing
can fail, a graded artifact no instruction asks for, and a universal IF with a
mechanism-specific THEN all pass `validate.py` and have each cost a lane-wide
repair.

After edits, run the validation and release-boundary checks under `tools/` before
publishing a release:

```bash
python tools/validate.py
python tools/verify_references.py
python tools/build_index.py
```

Indexes are optional generated navigation, not canonical dependency state.
