# Executable PASS authoring

status: active
owner: PASS/runtime
last_reviewed: 2026-09-19

`PASS_RUN.md` owns the human method. `PASS/pass.py` owns supported ordinary
source-authoring transitions and staged unit integration. Repository maintenance,
release packaging and SkillForge Code Apprenticeship use their own tools.

## Start and resume

Run commands from the unpacked project or repository root, using its Python
environment with `PASS/requirements.txt` installed:

```text
python PASS/pass.py resume --domain <authorized-domain> [--source <source-file>] [--run <run-directory>]
python PASS/pass.py start --source <source-file> --domain <authorized-domain>
python PASS/pass.py abandon --run <run-directory> --reason <explicit-user-instruction>
python PASS/pass.py status --run <run-directory>
python PASS/pass.py template --run <run-directory>
python PASS/pass.py present --run <run-directory>
python PASS/pass.py submit --run <run-directory> --phase <current-phase> --input <record.json>
python PASS/pass.py accept-preflight --run <run-directory> --decision <decision.json>
python PASS/pass.py revise-preflight --run <run-directory> --input <preflight.json>
python PASS/pass.py land --run <run-directory> --decision <decision.json>
python PASS/pass.py close-run --run <run-directory>

# Optional bounded unattended orchestration for this one source:
python PASS/source.py authorize --run <run-directory> --reason <explicit-user-instruction>
python PASS/source.py status --run <run-directory>
python PASS/source.py drive --run <run-directory>
python PASS/source.py report --run <run-directory>
# `advance` remains a low-level deterministic-gate command for diagnosis/tests:
python PASS/source.py advance --run <run-directory>
python PASS/source.py rebind-source --run <run-directory> --source <same-source-new-path>
python PASS/source.py revoke --run <run-directory>
```

`--repo-root <project-root>` may precede the command when running from elsewhere.
`--input -` and `--decision -` read a JSON object from standard input. Save generated
records and reading notes inside the owned task directory, not the workspace root.
`template` prints the current record with deliberately incomplete declarations;
edit it only after doing the authorized work. Unknown or missing record fields
fail the gate. Every phase record uses integer `schema_version: 1`; unit records
must name the only active `unit_id`.

`start` checks the source exists but does not read its content. It refuses to
open a second unfinished run of the same source in the same domain: it compares
the path and, when a run's recorded size matches, the SHA-256 of the bytes, so a
moved or renamed copy is still recognized. Abandoned and finished runs do not
block; another domain's run of the same book is independent. A domain must already own
a `MODULE.yaml`; an arbitrary folder is insufficient. In a multi-domain repo,
choose the domain explicitly from user authorization. The single authorable
domain of a bounded snapshot is the only automatic default. Never infer a new
package from a book's title, front matter or topic. Missing-domain rejection is
authoritative; domain creation requires a separate authorized maintenance task.

`start --task <book-run-slug>` optionally sets a unique lowercase task name. The
default derives a readable book name plus a unique suffix. Existing task paths
are never overwritten; resume with `--run`.

### Re-entry after context loss

`resume` is the front door for every fresh, compacted, restarted or switched
model context. It is read-only and derives everything from controller files;
the conversation's memory of the run is never consulted. Without `--run` it
searches the domain's unfinished runs, filtered by `--source` when given. None
found: it says to `start`. Several: it lists them and the user chooses; it never
picks one or starts another. One: it verifies and reports the run, source title,
units completed, current unit and phase, last accepted step, source identity and
draft state, then names the **one** next legal action and repeats the current
`status` brief.

`resume` fails closed, changing nothing, when:

- `controller/operation.lock` remains, meaning an operation was interrupted. The
  lock records its process ID and time. Confirm no PASS process is running and
  inspect the library and staged files before removing it.
- the bound source moved (it prints the exact `rebind-source` command when
  `--source` names identical bytes) or its bytes changed;
- staged files changed after PASS 3, or live cards changed after PASS 2 (it names
  the required `rewind`).

### Hard checkpoints and rollback

Every operation that changes `controller/run.json` ends at a **hard checkpoint**:
the controller copies the run's `drafts/` and `recipes/` into
`controller/checkpoint/`, bound to that exact state, and rewrites `HANDOFF.md`.
An operation that accepts nothing (`present`, `drive`) never moves the
checkpoint, so half-finished work is never captured as the safe endpoint.

A phase is atomic: it is either accepted or restarted. If a session stops inside
a phase, `resume` lists the drafts changed since the checkpoint and directs the
next session to `python PASS/pass.py rollback --run <run>`, which restores the
drafts exactly (changed files restored, new files removed) and leaves the phase
to be redone from its beginning. Stopping inside PASS 3 therefore returns to the
end of PASS 2; inside PASS 2, to the end of PASS 1 or its checkpoint; inside
PASS 1, to the unit's start. Never finish a phase another session left half
done, and never claim a read the current session did not do. Only the session
that made the edits, still inside the phase, keeps them.

`HANDOFF.md` is generated from controller state after every checkpoint: the last
safe endpoint, the current unit and scope, the drafts at the checkpoint and the
pick-up commands. Do not edit it. Notes worth carrying between sessions
(corrections, traps, discussion) go in `NOTES.md`, which the controller never
rewrites; a hand-written `HANDOFF.md` found in a run is moved there. Do not read
`controller/run.json` to orient: it is the controller's state, not a briefing,
and `resume`, `status` and `template` give what a session needs. PASS 2 stores
one fingerprint of the live library files it depends on rather than their full
hash map, which kept `run.json` hundreds of kilobytes large. In unattended mode `resume` directs the host to `source.py
drive`, which returns the unchanged lease when nothing was accepted and archives
a stale one before issuing its replacement. PASS cannot see the host's context
usage, so when to compact remains the host's or user's decision; `resume` makes
any compaction at an accepted step safe.

`abandon` retires an unfinished run only on the user's explicit instruction,
quoted in `--reason`. It moves the final state to `controller/abandoned-run.json`,
withdraws any action lease and keeps the drafts for inspection. An abandoned run
can no longer be resumed, and its source may be started again. Delete the
retained directory once it is no longer needed. A finished run is closed with
`close-run`, not abandoned.

```text
workspace/authoring/<domain>/<book-run>/
  RUN_NOTE.md
  controller/run.json
  drafts/<canonical-category>/PAT_<slug>.md
  drafts/<canonical-category>/AP_<slug>.md
  drafts/<canonical-category>/DRILL_<slug>.md
  drafts/<canonical-category>/assets/<image-and-sidecar>
  recipes/<existing-owned-SkillForge-recipe>.yaml
```

`drafts/poetry/sound/PAT_example.md` targets
`library/<domain>/poetry/sound/PAT_example.md`. Book identity stays in temporary
workspace organization; placement reflects knowledge, not the source. Cards use
the unchanged canonical schema and carry no source locators or controller hashes.
Drafts may be incomplete during PASS 1; only validated finished objects can land.

## Unattended single-source mode

`PASS/source.py` is the state-driven source-level dispatcher above the ordinary unit controller.
It exists for a user instruction such as: *run this PASS while I am away; continue
through each unit until I return*. Authorization is explicit, source-scoped and
bounded through that source's completion. The identity marker is created only after LOAD
passes; the duplicate check at `start` hashes bytes but records nothing. It is not standing permission for a
second book, another domain, or a later run.

The runner deliberately does **not** call a model or fabricate substantive PASS
records. The host still performs every required read and submits ordinary records
through `PASS/pass.py`. In unattended mode, `source.py drive` first issues a persisted action lease for each substantive phase; `PASS/pass.py` refuses that submission without the matching lease. `source.py advance` is the lower-level primitive that acts only at deterministic source
gates:

- at `preflight_accept`, render the complete preflight packet, save the exact bytes
  plus SHA-256 under `controller/audit/`, and consume the recorded unattended
  authorization to release PASS 1;
- at routine `land` where PASS 2 declared `approval_required: false`, render and
  audit the complete landing packet, then land it under `unattended authorization`;
- at `land` where `approval_required: true`, archive the packet and stop for the
  practitioner;
- at `finished`, run full-library `validate.py` and `verify_references.py` and
  record a source-completion marker.

Chat reproduction of audited packets is not required in unattended mode. This is
a token-saving presentation rule, **not** permission to omit the packet, hash,
PASS stage, or validation. Audit files are disposable authoring scratch and are
removed by `close-run`; inspect or export them before closing if needed.

Checkpoint routing remains semantic. Evidence-settled questions may be resolved by
the host and submitted normally. If any answer depends on practitioner judgment,
the run parks at that checkpoint. Unattended authorization never supplies a
missing practitioner answer and never consumes `approval_required`.

After the LOAD declaration passes, the controller records the source's SHA-256 and size. Every unattended gate verifies the
currently bound file against that identity. If a project-chat/container boundary
changes the path, `rebind-source` may update the path **only** when the new file's
bytes match the original identity. A different PDF cannot inherit the run.

## Accepted progression and records

1. **LOAD.** Read every current canonical document listed by `status` and submit
   their exact paths in `documents_read`, once each. A handoff is orientation,
   never a substitute. No source access is authorized before LOAD.
2. **Preflight.** Run exactly once for the entire source. Structural orientation
   only: metadata, contents, page map, extraction-quality sampling and
   instructional boundaries. Complete the generated preflight record, including
   subject, contiguous units, live active-domain overlap IDs, explicit forecasts
   and no-extract spans. Validation moves the run to `preflight_accept`, **not**
   PASS 1. Run `present` and reproduce the complete generated preflight packet,
   then wait for explicit user confirmation of the stated subject and provisional
   source-wide plan. The original request to run PASS is not that confirmation.
   After confirmation, generate the current template and submit it through
   `accept-preflight`; the decision must be hash-bound to the current packet,
   repeat the exact subject, use basis `user confirmation`, and include a reason.
   If the user requests a correction, submit a complete replacement record with
   `revise-preflight`, then `present` it again before acceptance. Once accepted,
   every later unit begins at PASS 1; there is no unit-level preflight. Only
   `unit ingestion` progression is supported. `curriculum audit` fails closed;
   the standalone old preflight helper cannot authorize it. `replan` is an
   evidence-backed amendment to remaining unit boundaries after acceptance, not a
   second preflight.
3. **PASS 1.** Read the entire current unit. Declare `full_read: true`, relative
   `working_drafts`, live `overlap_object_ids`, `secondary_subject_flags` and
   consequential `questions`. Flag entries are `{flag_id, subject}`; question
   entries are `{question_id, question}`. Their IDs are unique lowercase words
   with optional underscores. Use explicit `[]` when none. Working drafts must
   exist in the owned task; they do not enter the library yet.
4. **Checkpoint, when questions exist.** Submit `answers` entries
   `{question_id, resolution}` for every question. Report the actual practitioner
   answer or evidence-settled resolution permitted by the human rules. Do not
   invent an answer or treat elapsed time as approval. PASS 2 stays blocked until
   the checkpoint is resolved.
5. **PASS 2.** Reread the complete unit cold. Declare `full_reread: true` and
   resolve every flag with `{flag_id, reason}`. Every delta bucket must appear:
   `NEW_PATTERNS`, `REFINE`, `REINFORCE`, `VARIANTS`, `REPLACE`, `NEW_APS`,
   `NEW_DRILLS`, `REJECT`. Entries are `{object_id, reason}`; each object gets
   one disposition. Empty buckets are `[]`. Existing-owner dispositions resolve
   only inside the active domain; `REINFORCE` leaves the owner unchanged.
   All four taxonomy buckets appear: `NEW_SUBCATEGORY`, `MOVE`, `RENAME`, `MERGE`,
   each with `{path, reason}` entries or `[]`. Paths are relative to the domain.
   Declare exact task-relative `changes` and domain-relative `removals` lists.
   Changes may include cards, canonical module files, assets and their review
   sidecars, and the domain's existing recipe. Indexes cannot be staged or
   manually removed. A new category requires `NEW_SUBCATEGORY`; moving an ID
   requires explicitly removing its old path. Module changes include the owned
   canonical recipe in the same delta. `approval_required` is an explicit
   Boolean reflecting the applicable human rules; it does not grant approval.
   Asset support folders do not create knowledge subcategories. Ordinary runs
   update the existing canonical recipe's module list only, explicitly covering
   every active-domain module; release metadata/composition is separate maintenance.
6. **PASS 3.** Close the source and reading notes. Review the finished cards as
   standalone executable objects, repair defects and rescan. Declare
   `card_only_review: true`, every generated semantic check `true`, and the exact
   `reviewed_sha256` map for the files actually reviewed. The controller validates
   an overlay of the own domain plus `metaskills`, with replacements substituted
   for their live owners. Real schema, identity, asset and typed-relation checks
   supplement the semantic review. Untouched historical relation migration debt
   remains separate; edited cards and newly introduced defects must be clean.
   Module identities and any staged recipe's full prerequisite closure must
   resolve. Any failure leaves this unit active.
7. **Landing.** Run `present` first and reproduce its generated packet in full.
   `present` renders every disposition/taxonomy bucket (including empty ones),
   every reason, exact changes/removals, and approval status, then records a
   disposable packet SHA-256. Do not summarize the packet. After the applicable
   practitioner/evidence gate is actually satisfied, generate the landing
   template and submit `{schema_version, unit_id, presentation_sha256, basis,
   reason}`. The template leaves `basis` blank; fill it with exactly `user
   approval` or `evidence` only after the gate is satisfied. A delta marked
   `approval_required` accepts only `user approval`. The controller rejects a
   landing decision unless `present` ran for the current unit and the decision is
   bound to the current packet hash. It then checks the reviewed bytes and
   unchanged live owners, validates the complete repository overlay including
   global ID uniqueness, regenerates the active domain's indexes, verifies written
   bytes, and advances one unit directly to PASS 1 (or `finished` after the last
   unit). Ordinary write failures restore affected files and keep the unit open.
   Successfully integrated staged files are removed. Landing creates no Git
   commit; commit sizing and publication remain separate maintainer actions.

Read/reread declarations and semantic checks record the host's truthful work;
they are not proof of cognition. An unrestricted host can still access sources
or bypass scripts. Such work is outside the supported run protocol and must not
be represented as a valid PASS run. Do not edit `controller/run.json` to evade a
rejection or silently fall back to manual ingestion. Neither successful parsing
nor an accepted forecast makes a missing read valid.

## Recovery, independent books and cleanup

```text
python PASS/pass.py rewind --run <run-directory> --phase pass1
python PASS/pass.py rewind --run <run-directory> --phase pass2
python PASS/pass.py rewind --run <run-directory> --phase pass3
python PASS/pass.py rollback --run <run-directory>
python PASS/pass.py replan --run <run-directory> --input <amendment.json>
```

Rewind PASS 1 when source work needs repeating. Rewind PASS 2 when a disposition,
target identity or live owner changes, reconcile the full reread, then repeat
PASS 3. Rewind PASS 3 for card repairs that leave accepted PASS 2 dispositions
and targets valid. Editing staged files after an accepted PASS 3 blocks landing
until another scan is accepted. Status and templates resume the same unit across
sessions; a context boundary never splits it.

After preflight acceptance, instruction can revise the provisional unit scheme
before accepting the active unit's PASS 1. `replan` takes integer
`schema_version: 1`, a nonempty `reason`
giving instructional evidence, and a complete replacement plan in the existing
`preflight`-shaped field for backward compatibility. **This is a plan amendment,
not a rerun of preflight.** It may change remaining units/no-extract spans, but
never the source identity, subject, domain or any closed unit. Context pressure
is not instructional evidence, and `replan` does not authorize another
source-orientation read.

Several books may stage independently. They validate against the live library,
not copies accepted at the beginning of a source. A changed live card, asset,
shared prerequisite or canonical recipe invalidates an older review and requires
PASS 2 reconciliation. A transient `.landing.lock` in the domain's authoring
workspace serializes its integrations; the host serializes canonical merges
across domains. It is an exclusive lease, not shared research state or a history.
Per-run `controller/operation.lock` similarly prevents overlapping operations
on one task. Both are removed on normal completion. After an interrupted process,
inspect the library and verify no operation remains active before removing a
stale lease. A process termination during filesystem writes may require manual
reconciliation from preserved drafts; ordinary caught write failures roll back.

After all units land, `close-run` removes generated controller state and its
task note, prunes empty task directories and preserves nonempty retained work.
Preserve original inputs, other tasks and explicit failure-evidence holds. Remove
remaining owned scratch when its purpose ends, under `PASS_RUN.md`'s workspace
lifecycle. No controller state or drafts ship in project archives or SkillForge
releases. Deleting scratch never invalidates the accepted library. A returned
project archive lands changes normally through the existing snapshot importer;
workspace organization is not a new integration format.
