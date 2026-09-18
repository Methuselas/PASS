# Executable PASS authoring

status: active
owner: PASS/runtime
last_reviewed: 2026-09-18

`PASS_RUN.md` owns the human method. `PASS/pass.py` owns supported ordinary
source-authoring transitions and staged unit integration. Repository maintenance,
release packaging and SkillForge Code Apprenticeship use their own tools.

## Start and resume

Run commands from the unpacked project or repository root, using its Python
environment with `PASS/requirements.txt` installed:

```text
python PASS/pass.py start --source <source-file> --domain <authorized-domain>
python PASS/pass.py status --run <run-directory>
python PASS/pass.py template --run <run-directory>
python PASS/pass.py submit --run <run-directory> --phase <current-phase> --input <record.json>
python PASS/pass.py land --run <run-directory> --decision <decision.json>
python PASS/pass.py close-run --run <run-directory>
```

`--repo-root <project-root>` may precede the command when running from elsewhere.
`--input -` and `--decision -` read a JSON object from standard input. Save generated
records and reading notes inside the owned task directory, not the workspace root.
`template` prints the current record with deliberately incomplete declarations;
edit it only after doing the authorized work. Unknown or missing record fields
fail the gate. Every phase record uses integer `schema_version: 1`; unit records
must name the only active `unit_id`.

`start` checks the source exists but does not read it. A domain must already own
a `MODULE.yaml`; an arbitrary folder is insufficient. In a multi-domain repo,
choose the domain explicitly from user authorization. The single authorable
domain of a bounded snapshot is the only automatic default. Never infer a new
package from a book's title, front matter or topic. Missing-domain rejection is
authoritative; domain creation requires a separate authorized maintenance task.

`start --task <book-run-slug>` optionally sets a unique lowercase task name. The
default derives a readable book name plus a unique suffix. Existing task paths
are never overwritten; resume with `--run`.

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

## Accepted progression and records

1. **LOAD.** Read every current canonical document listed by `status` and submit
   their exact paths in `documents_read`, once each. A handoff is orientation,
   never a substitute. No source access is authorized before LOAD.
2. **Preflight.** Structural orientation only: metadata, contents, page map,
   extraction-quality sampling and instructional boundaries. Complete the
   generated preflight record, including subject, contiguous units, live
   active-domain overlap IDs, explicit forecasts and no-extract spans. Only
   `unit ingestion` progression is supported. `curriculum audit` fails closed;
   the standalone old preflight helper cannot authorize it.
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
7. **Landing.** Present the full delta and reasons. Submit `{schema_version,
   unit_id, basis, reason}`, with basis exactly `user approval` or `evidence`.
   Record actual authorization or the evidence-settled basis permitted by the
   method. A delta marked `approval_required` accepts only `user approval`.
   The controller checks the reviewed bytes and unchanged live owners, validates
   the complete repository overlay including global ID uniqueness, regenerates
   the active domain's indexes, verifies written bytes, then advances one unit.
   Ordinary write failures restore affected files and keep the unit open.
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
python PASS/pass.py replan --run <run-directory> --input <amendment.json>
```

Rewind PASS 1 when source work needs repeating. Rewind PASS 2 when a disposition,
target identity or live owner changes, reconcile the full reread, then repeat
PASS 3. Rewind PASS 3 for card repairs that leave accepted PASS 2 dispositions
and targets valid. Editing staged files after an accepted PASS 3 blocks landing
until another scan is accepted. Status and templates resume the same unit across
sessions; a context boundary never splits it.

Instruction can revise the provisional unit scheme before accepting the active
unit's PASS 1. `replan` takes integer `schema_version: 1`, a nonempty `reason`
giving instructional evidence, and a complete replacement `preflight`. It may
change remaining units/no-extract spans, but never the source identity, subject,
domain or any closed unit. Context pressure is not instructional evidence.

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
