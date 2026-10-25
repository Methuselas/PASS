# Changelog

PASS follows [Semantic Versioning 2.0.0](https://semver.org/). This file records
user-visible changes to the PASS factory contract. Individual SkillForge
skillsets may evolve independently.

## Unreleased

## 1.0.0-beta.138 - 2026-10-24

### Fixed

- **The generated SkillForge `SKILL.md` Skillset Memory section no longer
  describes a claim as an observation (residual post-R2 wording correction).**
  beta.137 restated the section's opening as the current learned state and moved
  its vocabulary from the retired `entry` to `claim`, but it left the clause
  "read each claim as an observation carrying a stated confidence". The final R2
  defines a claim as a **learned proposition**, not an observation, so that
  clause still contradicted the contract it was meant to state. The clause now
  reads "read each claim as a learned proposition carrying a stated confidence,
  not as an instruction". Only that generated sentence changed: retrieval,
  confidence, projection behavior, schema, corpus, packaging, and Tesseract are
  all untouched. A regression gate on the existing learned-versus-history test
  now holds the generated section to the not-an-observation rule, scoped to the
  claim description rather than a repository-wide ban on the word.

## 1.0.0-beta.137 - 2026-10-24

### Fixed

- **The generated SkillForge `SKILL.md` no longer misdescribes Skillset
  Memory as empirical history (post-R2 producer wording correction).** The
  release generator's Skillset Memory section opened by calling
  `memory/<domain>/skill_memory.yaml` "this skillset's **empirical record**:
  what actually happened when this canon was used" and told the reader to
  "read each entry as an observation" - wording that reverses the final R2
  authority split, where Skillset Memory is the current learned state and
  Training History is the empirical record of concrete attempts. The section
  now states what it is: the skillset's current learned state about doing the
  skill's work, carried as claims, not canon, with the release copy a
  current-state projection that omits claim-level `evidence` and ships no
  `training_history.jsonl`. No release mechanics, schema, or claim data
  changed; a focused regression gate holds the generated section to the
  learned-versus-history distinction and the claim vocabulary.

## 1.0.0-beta.136 - 2026-10-24

### Fixed

- **The root `README.md` no longer teaches the retired pre-R2 Memory
  architecture (T22 correction).** The landing page escaped criterion 1's
  governed-surface scan, but it states the Memory contract in present-tense
  instructional prose, so it is T22-owned. Its Memory passages now state the
  schema-3 claim contract - current learned claims classed `conduct` or
  `reach`, with card candidates in
  `canon_workflow/<domain>/card_candidates.yaml` rather than in Memory - and
  the CRQ walkthrough now starts from an open candidate in that store with
  the live `prepare --candidate` interface instead of the dead
  `--memory-entry` invocation that read Skillset Memory. A narrow regression
  gate holds the root README to the same retired-vocabulary rule the governed
  documents face, without redefining criterion 1's surface list.

## 1.0.0-beta.135 - 2026-10-24

### Changed

- **Every document that states the Skillset Memory contract now states the
  schema-3 claim contract (T22).** The runtime moved to claims over T01-T21, but
  the prose a reader reaches first still described the retired shape, so the
  repository carried two contradictory specifications of the same store. This is
  contract correction, not documentation tidying: a reader who followed
  `MEMORY_SCHEMA.md` section 5 would have written an entry with a `type`, a
  `status`, and an `evidence_count` into a store whose validator rejects all
  three.

  `MEMORY_SCHEMA.md` is the principal change. The v1/v2 store shape, the
  required/optional entry keys, the two promotion thresholds, the five-state
  lifecycle, specialization profiles, card-candidate incubation, and compaction
  are deleted; the claim contract is promoted to section 5 and is now the whole
  current Memory contract. Retrieval is restated for v3 as its own section, and
  self-containment is kept, re-pointed from the entry to the claim. The four
  test-locked phrases survive verbatim, including the invalid-run invariant,
  which now says an invalid event must never increment *the weight of evidence
  standing behind a claim* rather than naming the retired `evidence_count`.

  The hard rule in `CLAUDE.md` and `AGENTS.md` keeps its bold lead byte for byte
  and replaces the prose after it: claims, `conduct` and `reach`, currentness as
  presence, retirement as removal, and `confidence` as maturity that is never
  mechanically derived. `ARCHITECTURE.md` contract 20 drops the four retired
  types and states what a release actually ships - the current-state projection
  only, with representative `evidence` stripped and no Training History beside
  it.

- **The candidate workflow is documented where it actually lives.**
  `CANDIDATE_REFINEMENT.md` described CRQ intake as resolving a `card_candidate`
  out of Skillset Memory, which T10/T11 re-homed to
  `canon_workflow/<domain>/card_candidates.yaml` and the controller has read
  from ever since. The intake section, the disposition vocabulary
  (`candidate_action`, not the retired `memory_action`), and the
  `SOFTWARE_CARD_FIELD_TESTS.md` repair pipeline now name that store. Skillset
  Memory is stated as what it is on this path: not a CRQ input.

### Fixed

- **`MODULE_RELEASES.md` no longer promises a legacy pass-through that T21
  deleted.** It said a store of any older schema ships whole with its History;
  packaging has one branch and projects schema 3, and a store of any other
  declared schema stops the build.

- **`memory/README.md`'s current-contract defects.** It opened by describing
  Skillset Memory as "what actually happened when the canon was used", which is
  Training History; it said `build_release.py` "copies the store", which
  predates the T09 projection; it called Memory "the record of using the canon";
  and it claimed the Art store is seeded with three craft observations, which
  the migrated store is not. The separately deferred wording question in the
  directory tree is untouched.

- **The anti-inline firewall runs against claims.** `test_memory_is_not_inlined_into_canon`
  iterated `entries` and compared `observation`, so after the migration it
  passed over an empty list and proved nothing. It now reads `claims` and checks
  both prose fields a claim carries - `claim` and `delta.statement` - against
  every card and skill entrypoint.

### Added

- `test_memory.py::ContractDocuments`, two gates over the documents that state
  the contract: no governed current document presents retired schema vocabulary
  as a current Memory schema value, and every `memory.py <word>` it names is a
  live subcommand read off the tool's own parser. Neither is a repository-wide
  string ban. Ordinary English is not banned - `status:` front matter and "awaits
  diagnosis" both stand, because the ambiguous tokens are caught only as keys
  inside a fenced block describing a Memory store - and a sentence that declares
  a name retired is permitted, which is what lets the S2 rule row list the
  legacy-only keys it rejects and lets "There is no `supersede`" state the
  contract. `workspace/handoffs/` and Training History are outside both gates:
  rewriting the migration evidence to match the present would destroy the record
  the migration was judged on.

## 1.0.0-beta.134 - 2026-10-24

### Fixed

- **Every current-store reader now passes through one authoritative schema
  gate, so none of them can consume a store before its runtime schema state has
  been classified (T21 correction).** beta.133 put the runtime on schema 3
  alone, but the check that enforced it was per-command, and three reading paths
  disagreed with each other and with the validator. An independent review
  reproduced all three.

  `query` asked only whether the declared version was a *retired* one. A store
  declaring `memory_schema_version: 4` therefore retrieved normally — claims
  returned, ordinary receipt, exit 0 — while `validate` called the same file an
  unknown version. `show` asked nothing at all: on a v1 or v2 store it reported
  `no claim '<id>'`, which says a claim is absent from a store whose claims this
  runtime cannot read, and on a legacy-declared mapping that happened to carry a
  `claims` key it printed the claim and exited 0. That was a runtime path
  reading v1/v2 content, which beta.133 states does not exist.

  The fix is one seam rather than three checks. `load_current_store` loads a
  store only after classifying it, and `query`, `query_v3_store` and `show` call
  it instead of `load_memory`; `unsupported_version_problem` is the third
  refusal beside `unmigrated_problem`, so an undefined version never borrows the
  migration wording and a retired one never reads as unknown. The write path
  already enforced the exact version and is unchanged. `validate` and `review`
  keep their own error channels and their existing messages.

- **A domain directory with no `skill_memory.yaml` in it is absence, not a
  failure.** Fail-open covers no store, no domain, and an empty store (R2.5
  §9.2), and this topology is the first of those: the directory can be left
  behind by a partial copy or a domain nothing has written yet. The named-domain
  lookup accepted the directory on `is_dir()` alone while the unnamed sweep
  required the store file, so a query with `--domain` reached the loader for a
  file that was not there and exited non-zero with no receipt. `domain_dirs` now
  applies one predicate both ways in, and the query answers `retrieved: (none)`
  at exit 0 as it already did for a missing root or a missing domain.

  Four runtime states stay exactly distinct, and a test drives one command
  through all four: absent (exit 0, honest empty receipt), unmigrated 1 or 2
  (non-zero, *unmigrated, not corrupt*), unsupported 4 or otherwise undefined
  (non-zero, unknown-version error, no migration wording), and schema 3 (the
  normal path). A parseable but schema-invalid v3 store stays deferred (R2.3 #3,
  R2.5 §12.11): this correction defines no corruption policy.

### Testing

- New `test_memory.py::SchemaContract` tests, each failing against beta.133 for
  the behavior it describes: `test_a_legacy_store_shaped_like_a_current_one_is_still_refused`
  (a legacy-declared store carrying `claims`, through `show` and `query`),
  `test_an_unsupported_version_is_refused_by_every_reader` (schema 4 through
  `query`, `show`, `validate` and `review`),
  `test_an_existing_domain_directory_with_no_store_is_absence`, and
  `test_the_four_runtime_schema_states_stay_distinct`, which exists to catch a
  shared gate widened to make one case pass.

- `show` joined `SchemaContract.unmigrated_commands`, the command/version matrix
  that beta.133 ran over every other reading command. Its omission is why the
  bypass shipped, and the matrix checks the store's bytes afterwards.

- `V3RetrievalSurface` now allows `load_current_store` and no longer allows
  `load_memory`: retrieval may not open a store ungated.

## 1.0.0-beta.133 - 2026-10-24

### Removed

- **Skillset Memory now reads one schema, and every transition scaffold that
  made two schemas possible is deleted (T21).** All four stores reached
  `memory_schema_version: 3` at beta.132, which was the condition R2.5 set for
  this cutover: no legacy store, path, or fixture could be removed until the
  gates that depended on it had passed.

  Gone from `PASS/tools/`: `memory_legacy_input.py` (the migration-input reader,
  a transition scaffold rather than a compatibility feature — Decision 1) and
  `migrate_memory_v3.py` (the one-time migrator). Gone from `memory.py`: the
  schema dispatch, `score_entry`, `query_store`, `review_legacy_store`,
  `STALE_DAYS`, `ENTRY_REQUIRED`, `RETRIEVABLE_STATUS`, `ID_RE`, the duplicate
  `FAILURE_LAYERS` that T12 had already re-homed to
  `PASS/runtime/candidate_qualification/schemas.py`, and `query --scope-id`, the
  legacy spelling of `--scope`. Gone from `build_release.py`: the `stage_memory`
  pass-through that shipped a non-v3 store whole (Decision 2 — one deletion
  ticket, no permanent conditional). `stage_memory` now has exactly one branch
  and it projects schema 3.

  Both deleted tool paths joined
  `test_architecture.py::test_retired_authoring_infrastructure_is_gone`, so
  neither can return quietly.

### Changed

- **A v1 or v2 store is refused as unmigrated, not corrupt.** Every command that
  reads a store — `validate`, `query`, `review`, `add`, `update`, `retire`,
  `link-evidence` — exits non-zero naming the store path, the declared version,
  the schema-3 contract in `PASS/docs/MEMORY_SCHEMA.md`, and the retired
  migrator that is recoverable from repository history. The word is
  *unmigrated*: the bytes may be perfect and the fix is a migration rather than
  a repair. Nothing upgrades a store in place, and the message is deliberately
  not generalised into a corruption policy — a parseable but schema-invalid v3
  store stays deferred (R2.3 #3, R2.5 §12.11).

  Fail-open is unchanged and is now stated beside its opposite. A missing
  `memory/` root, a missing domain, and an empty store each exit 0 with an
  honest empty receipt, because nothing in PASS may stop because Memory is
  absent. A wrong-version store is *presence*, not absence — it asserts that
  learned state exists while being unreadable — so it is always loud. An
  undefined version such as 4 is still the unknown-version validation error, and
  reads differently from unmigrated.

- **`memory.py validate` counts claims.** The summary counted `entries`, so
  every migrated store reported zero content and the printed total under-reported
  the corpus; beta.130 recorded the gap and left it here. The live corpus now
  reports `4 store(s), 127 claim(s), 308 event(s) validated`. A store with no
  History file beside it contributes no events rather than a missing-file error,
  which is what absence means beside a v3 store (I5).

- **`PASS/docs/MEMORY_SCHEMA.md` §10 and `memory/README.md` state the cutover.**
  Both described a dispatch that routed v1/v2 to a reader that no longer exists.
  §10's status line now records that schema 3 is live and sole; sections 5 and 7
  still describe the retired shape and are explicitly marked as describing no
  store that exists, because deleting them is T22's.

### Testing

- New `test_memory.py::SchemaContract` tests: `test_a_v1_store_is_loudly_unmigrated`,
  `test_a_v2_store_is_loudly_unmigrated` (both driving every reading command and
  checking the store's bytes afterwards), `test_unmigrated_is_not_corrupt`,
  `test_absence_is_still_silent_and_fail_open`, and
  `test_no_runtime_path_parses_schema_one_or_two` — the last read off the syntax
  tree, locking the retired version numbers to the single function that builds
  the refusal. `ShippedStore::test_no_legacy_store_remains_in_the_working_tree`
  asserts criterion 48 over the whole repository rather than over `memory/`.

- **The R2.5 §8.2 reversals landed.** Obsolete and removed, each for the reason
  §8.2 gives: `test_learned_principle_is_an_accepted_memory_type`,
  `test_v2_accepts_specialization_profiles_and_card_candidates`,
  `test_v1_rejects_v2_only_entry_types`,
  `test_superseded_status_requires_a_successor`,
  `test_unknown_evidence_origin_is_rejected`,
  `test_human_teaching_is_a_recognized_evidence_origin`, and
  `test_evidence_count_must_match_cited_events`. Surviving in spirit:
  `test_unknown_schema_version_is_rejected`, which now also asserts that the
  unknown-version message and the unmigrated message are different.
  `test_stage_memory_copies_a_legacy_store_untouched` and
  `test_projected_store_problems_passes_a_legacy_store` — the two further
  reversals scope recovery identified — are replaced by
  `test_stage_memory_refuses_a_store_it_cannot_project` and
  `test_projected_store_problems_reports_a_store_of_another_schema`.

- **Entry-shaped duplicates were retired rather than re-pointed.** The v1/v2
  contract classes stated things the v3 suites already state against the only
  claim schema there is, so `TemporaryStateFirewall` (covered by
  `V3Leakage::test_retired_authoring_and_lineage_keys_are_rejected` and
  `test_conversation_deference_is_rejected`), the entry-shape half of
  `SchemaContract` (covered by `V3Schema` and `V3ClaimInvariants`), and the
  entry-citing half of `AdmissibilityContract` (covered by
  `V3ReferentialIntegrity`) are gone. Each surviving class names where its old
  statements went. `AdmissibilityContract` keeps the Training History half,
  which is unversioned (R2.5 §8.4) and so crossed the cutover unchanged.
  `SchemaDispatch` became `CorpusSurface`: its four mixed-state tests described
  an arrangement the cutover removed, and what survives is the two-channel
  validate run plus a new `test_the_summary_counts_claims_across_every_store`.

- **`tests/test_memory_migration.py` is deleted with the migrator it tested.**
  2,440 lines covering FREEZE, hash verification, the sentence inventory, the
  A1–A10 accounting checker, the three reports, and the VERIFY gate — every one
  of them driving `migrate_memory_v3.py`. A suite for a deleted tool is not
  coverage.

### Owner decision recorded

- **`SpecificationExamples` is removed, not restored.** Two committed statements
  prescribed opposite dispositions for that suite: the beta.130 T20 entry said
  restoring its worked examples against a committed fixture "is T21's", while
  `test_memory_migration.py` and the beta.129 T17 entry said T21 removes the
  suite when the last domain migrates. The authoritative T21 ticket is silent,
  so the conflict went to the owner, who ruled: **remove the suite, and do not
  restore it against a committed v1/v2 fixture.**

  The beta.130 statement was an erroneous carry-forward note and is not T21
  authority; it stays in the changelog as historical evidence of the mistake
  rather than being rewritten. The ruling follows from what the suite was for —
  it read two *live legacy* entries, `SE_MEM_001` and `GAMEDESIGN_MEM_001`, and
  T17 and T20 consumed both — and from criterion 48, which is read literally: a
  committed test fixture that is itself a v1/v2 Memory store is a legacy store
  in the working tree. Restoring the examples would have preserved a transition
  scaffold inside the ticket whose whole subject is removing them.

  So: no committed legacy fixture is retained anywhere. The wrong-version tests
  synthesize minimal v1/v2 input inside their own temporary directories, which
  is test input rather than a retained store, and no production path parses it
  as a supported schema. A9 derivation coverage retired with the migrator it
  belonged to.

### Already satisfied, reconciled honestly

Three scope items were closed before this ticket began, and are recorded rather
than re-done:

- `FAILURE_LAYERS` was re-homed by T12 to
  `PASS/runtime/candidate_qualification/schemas.py`; verified that nothing
  imports it from a deleted module, and the dead duplicate in `memory.py` was
  removed with the other legacy constants.
- Criterion 48 was already satisfied for the four live stores at beta.132; what
  this ticket added is the repository-wide assertion that keeps it satisfied.
- The seven `SchemaContract` reversals R2.5 §8.2 names were all present and were
  reversed here by name.

Two items are explicitly **not** done, and neither is a gap: `MEMORY_SCHEMA.md`'s
legacy sections belong to T22, and the FREEZE inputs and signed ledgers under
`workspace/handoffs/` are untracked migration evidence this ticket is forbidden
to delete. They are the owner's to release; nothing active reads them and no
release ships them.

### Validation

`python -m unittest discover -s tests -p "test_*.py"` green.
`python PASS/tools/validate.py`, `verify_references.py`, and
`memory.py validate` over all four v3 stores green, with no FLAG unreviewed. A
transcript of a v1 fixture refused loudly by `validate`, `query`, `review`, and
`add` — with the fixture byte-identical afterwards — and an absent `memory/` root
accepted silently at exit 0, is reproduced by
`SchemaContract.assertLoudlyUnmigrated` and
`test_absence_is_still_silent_and_fail_open`. `PASS/tools/` carries neither
deleted module.

## 1.0.0-beta.132 - 2026-10-24

### Changed

- **The last T20 scenario resting on a lexical proxy is reclassified from MIXED
  to DECISION, and the claim it carried ceases to be executed.** A targeted
  re-review of beta.131 confirmed the three other blocker fixes and reproduced
  the corrected edit-history figures independently, then found that the proxy
  correction had missed one instance of the very error it was correcting.

  `fixtures/f_verification_batches.py` assigns a card an assertion *kind* by
  phrase regex. A non-match was being promoted into the semantic assertion that
  **35 of 202 C++ cards make no assertion a compile-or-run probe can decide**,
  and `SE_MEMORY_BEHAVIOR_TESTS.md` offered that census as the sole executed
  support for the claim that unreachable content must be scored untested rather
  than passing. The census survived the first correction because it looked like
  a count rather than a rate - 35 cards, enumerated, not sampled. The count is
  real; what it counts is not probe reach.

  **One member of the bucket refutes it by compiling.** The classifier assigns
  the empty kind set to `PAT_never_redefine_inherited_default_parameter`, whose
  Pattern Rule and `Don't` section assert that a call through a base-typed
  reference selects the derived virtual body and the base default argument -
  directly executable C++. The probe is carried as
  `fixtures/f_probe_reach_counterexample.cpp`:

  ```
  cl /nologo /std:c++20 /EHsc /W4 f_probe_reach_counterexample.cpp    exit 0
  base-reference=21 derived-reference=22                              exit 0
  ```

  21 is the derived body carrying the base default. Five further unmatched cards
  plainly assert executable behaviour - the short-circuit and comma operators,
  the `std::async` launch policy, postfix increment in terms of prefix, a
  non-virtual redefinition, constant-time erase into the hole - and the harness
  now lists them unadjudicated so that no count is drawn from them.

  The classifier is kept as a detector and its result renamed to what it
  establishes, **classifier-unmatched cards**, supporting no claim. No census of
  probe reach was run: settling it means reading all 35 cards, which is a sweep
  and not a migration step, and no other fixture in the set bears on the claim.
  Truthful downgrade was preferred to manufacturing evidence for the old label.

  | | EXECUTED | MIXED | DECISION | claims on reasoning evidence alone |
  |---|---:|---:|---:|---:|
  | beta.130 | 39 | 2 | 1 | 7 of 81 |
  | beta.131 | 37 | 4 | 1 | 12 of 81 |
  | **beta.132** | **37** | **3** | **2** | **13 of 81** |

  The scenario total stays 42 and section 3a of the evidence artifact gains a
  fourth proxy row, so every row of its index can still be checked against the
  rule it states.

- **No claim changed, and the store is not rewritten.** No claim text, delta,
  envelope, evidence citation or identifier was touched, `memory_version` stays
  63, and the builder reproduces the installed software-engineering store byte
  for byte (SHA-256 `29ec1211d436ba2e85a496f917133b09de886749f94904a6c2f78ebd2418ef1e`).
  The frozen legacy bytes verify against their FREEZE digest. The accounting is
  unchanged: 46 entries, 146 propositions, 146 dispositions, 127 survivors, 81
  claims, 19 signed losses, zero HOLDs, zero FLAGs. No disposition,
  decomposition, loss item, duplicate adjudication or Canon verdict was touched;
  the beta.131 fixes to the three other blockers are left exactly as they stood;
  T17, T18 and T19 were not reopened; T21 is not started. This is an evidence
  classification correction, not a regression in migration quality.

## 1.0.0-beta.131 - 2026-10-23

### Fixed

- **A T20 claim reversed the empirical result it was written from, and is
  corrected.** `SE_MEM_5628P29ZTEVVZASMYW7FTJ6YKG` said a behaviour credited to
  a support on four self-reports *did not survive the support being withheld*.
  The frozen legacy entry `SE_MEM_016` and event `SE_EV_0041` record the
  opposite: five candidate supports were withdrawn one or two at a time and the
  behaviour survived every removal, including the arm with none of the five
  present. What did not survive withholding was the **credit given to
  retrieval**. The claim now states that the ablation refuted the attribution
  and left the behaviour standing, which also removes a contradiction with the
  neighbouring reach claim recording the same persistence. The duplicate-matrix
  row that distinguishes this claim from the independent-validation claim was
  re-run against the corrected wording and is unchanged: the correction changes
  what the ablation refuted, not the condition under which the claim fires.
- **A claim asserted a cause its experiment did not establish.**
  `SE_MEM_AXTNZ3499FNCZRZC3DGSVQTVZC` held that where one density metric
  separates author kinds, *the separating variable is vintage or size*. The
  seven-corpus measurement reproduces - the within-kind spread exceeds the
  between-kind gap on two of three metrics, and runtime-check density separates
  the sampled groups at a 2.82 gap against a 0.79 spread - but nothing in it
  measured vintage or size. Those corpora are also the newest and the smallest,
  so the three vary together. The claim now reports two of three exactly, states
  the separation on the third as observed, and names vintage and size as
  **confounds preventing attribution** rather than as demonstrated causes.
- **Two claims rested on predictive language a rerun did not establish.**
  `SE_MEM_DPPP6562EDPMYN6FW5GY5CKT9M` began "What predicts a broken claim about
  what the language requires...", excluding claim kind and raw age. The rerun
  measured **edits per card**, not broken-claim frequency, and the series is
  non-monotone (1.42, 2.31, 1.64, 2.71, 1.47 by source distance). The claim is
  rewritten to the scoped historical observation its own batch evidence
  supports - the nine batches whose source provenance was known - and the
  predictive framing is gone; the companion claim's stale condition,
  which asserted source distance *predicts* better than claim kind, is corrected
  to the same historical form, and both now carry the edit measurement in their
  envelopes as an explicitly non-equivalent proxy.

### Changed

- **Two behaviour scenarios are reclassified from EXECUTED to MIXED, because
  their harnesses measured proxies and the evidence reported the proxies as the
  thing they stood for.** This supersedes the beta.130 figures.

  | | EXECUTED | MIXED | DECISION | claims on reasoning evidence alone |
  |---|---:|---:|---:|---:|
  | beta.130 | 39 | 2 | 1 | 7 of 81 |
  | **beta.131** | **37** | **4** | **1** | **12 of 81** |

  The drill-specification sweep flagged 262 of 472 graded requirements as
  "unbacked" on a word-overlap heuristic, and the evidence called them 262
  specification defects. A hand adjudication of fifteen flags drawn at even
  intervals from the sorted flag list, each read against its drill's own
  instruction steps, **confirmed none**: thirteen are false positives and two
  requirements carry one unasked element each. One drill has all six of its
  requirements flagged while its instructions ask for the graded work step by
  step, and the lowest-overlap flag in the sample is also a false positive, so
  the cut point is not the problem. The sweep is now reported as 262 **candidate
  flags** at a measured precision of zero, which converts it into a second
  executed instance of the claim that a keyword proxy for a non-decidable
  property reports noise - the one claim that scenario does establish. The other
  two return to reasoning evidence.
- The repair-history harness counted every post-introduction commit as a repair
  and every commit sparing the IF/THEN marker lines as illustration-only,
  yielding "411 of 462 (89 %)". Both were wrong. **173 of the 462 edits never
  leave the YAML front matter** - the worked example changes a foundation role
  and one cross-link - and the marker regex under-counts rule edits by 2.7×,
  because a rule can be reworded without its markers changing. Classified by
  section over the pattern cards: 360 edits, 152 metadata-only, and of the 208
  prose edits **152 (73 %) leave the rule untouched**. The harness now keeps
  *edit*, *metadata edit*, *rule edit*, *repair* and *probe failure* as five
  separate terms in its own header, and records that git holds the first three
  and neither of the last two. Three claims about probe outcomes across twenty
  verification batches return to reasoning evidence; the corpus census of what a
  probe cannot reach stays executed, because the repository does answer it.
- `memory/software-engineering/skill_memory.yaml` declares `memory_version: 63`.
  The store is regenerated from the same frozen legacy bytes and the same
  recorded claim-id map, so every claim id is unchanged and the four corrected
  claims are the only content difference.

### Known issues

- **Twelve of 81 claims rest on a reasoning fixture alone**, up from seven: the
  seven beta.130 recorded, plus the two whose lexical cross-reference does not
  implement the semantic one they describe, plus the three about probe outcomes
  across twenty verification batches that git cannot see. Each is recorded with
  why it cannot be executed and the strongest experiment run in its place.
  Adjudicating all 262 flags by hand would execute one of the two; re-running
  twenty verification batches against the C++ module would execute the three,
  and that is a sweep rather than a migration step.
- The migration accounting, Canon ownership, loss accounting, cutover, domain
  isolation, duplicate dispositions and the `SE_MEM_003` / `SE_MEM_016`
  adjudication are unchanged and were not reopened: 46 entries, 146
  propositions, 146 dispositions, 81 claims, 19 signed losses, zero HOLDs.
  Full discovery and the skip baseline are unchanged from beta.130.

## 1.0.0-beta.130 - 2026-10-23

### Changed

- **The software-engineering Skillset Memory store is migrated to schema 3,
  completing the four-domain migration (T20).** All four domains now declare
  `memory_schema_version: 3`; no legacy store remains in the corpus. The
  migration was gated on an empirical requirement the three earlier domains did
  not carry: every surviving claim had to be put against a fixture exercising
  real code or repository behaviour, not a prose fixture.
- **Accounting.** **46 legacy entries** decomposed into **146 propositions**,
  which received **146 dispositions** - REWRITE 124, EXTRACT 3, REHOME 1,
  REJECT 18 - of which **127 survive** and resolve to **81 live claims**. The
  gap is 46 redirections where several source propositions collapse onto one
  claim; there are no splits. Losses: **19** items (18 rejections, 1
  re-homing), each signed individually with its own note; **zero** HOLDs and
  **zero** FLAGs. The **508** sentences of the forty-six entries' `observation`,
  `boundary` and `diagnosis.hypothesis` are each accounted exactly once.
  Thirteen entries were classified as in-place accretion and all thirteen went
  to an independent blind second reader. The store declares
  `memory_schema_version: 3` and `memory_version: 62`.
  `memory/software-engineering/training_history.jsonl` is byte-identical to its
  FREEZE hash at **124 events**, and the art, game-design and writing stores are
  byte-identical to their pre-T20 hashes.
- **The empirical layer is now executed rather than reasoned.** Forty-two
  behaviour-test scenarios back the 81 claims: **39 EXECUTED, 2 MIXED, 1
  DECISION**, against 25 EXECUTED and 17 DECISION before this pass. Claims
  resting on a reasoning fixture alone fell from **37 of 81 to 7 of 81**. The
  conversions are real measurements over real artifacts - 378 core patterns
  swept for rule-position defects, 102 drills cross-referenced against their own
  grading standards, seven C++ corpora re-measured for check and comment
  density, 202 C++ cards against 462 git repair commits, a fail-closed gate run
  against two phrasings of one violation, `validate.py` line-traced over 2 388
  objects, and four contract seams rebuilt and run.
- **Three claims were changed because the measurements disagreed with them.**
  `T_008_1` claimed the within-kind spread exceeds the between-kind gap *on
  every metric*; re-measurement over seven corpora found it holds on two of
  three, and the claim is narrowed with the confound named. `T_022_2` claimed a
  count derived from a structure survives re-measurement; byte sizes reproduced
  exactly but an element-move count did not, because the container growth factor
  is an implementation choice, so the claim now draws the line between what a
  structure fixes and what an implementation fixes. `T_025_2` claimed source
  distance predicts a broken language claim; it holds at the extremes
  (2.71 repairs/card at distance 4 against 1.42 at distance 0) and fails in the
  middle, so the claim is narrowed to aiming a batch rather than ranking one. A
  fourth measurement - language-requirement cards showing the *highest* repair
  rate, against `T_025_1`'s ordering - is recorded without changing the claim,
  because repair frequency is a proxy for probe failure and a card is touched
  for other reasons.
- **The duplicate matrix is reproducible.** All five `duplicate_of` rejections
  now rest on an executed discrimination that would have separated the pair had
  they been distinct; two of the five previously rested on reading. A sixth row
  records a pair that is *not* a duplicate, with the two evidence configurations
  that separate it.
- **The `SE_MEM_003` / `SE_MEM_016` adjudication is closed, and no owner
  decision remains.** The two entries declare the same `scope_id` and are
  distinct boundaries on it: 003's content was absorbed into
  `AP_review_code_you_did_not_write` between its sighting and this migration -
  six of seven propositions are now Canon text verbatim, checked clause by
  clause - while 016's nine survive as six claims because step 5, step 7 and
  `PAT_look_for_the_evidence_outside_the_code` do not carry them. Nothing was
  merged across the two entries, nothing was chosen for being newer, and neither
  was retired.

### Fixed

- Three migration tests pinned the live software-engineering store as a legacy
  migration input - the last such store in the corpus. They now assert the
  firewall that matters after T20: FREEZE and the sentence emitter must *refuse*
  a schema-3 store rather than re-freeze or slice it, which is the only way a v3
  store could be migrated twice. The mechanics the live store exercised are
  preserved synthetically, including the overlap case where an event is both
  invalid and quarantined and must be excluded once rather than twice.
- A T20 behaviour fixture resolved `PASS/tools/memory.py` relative to the
  caller's working directory, so it only ran from the repository root. It now
  resolves from its own location.

### Known issues

- **The full-discovery skip baseline moves from 2 to 3.** `SpecificationExamples`
  draws its A9 end-to-end examples from the two live legacy entries R2.5 7.2
  names, `SE_MEM_001` and `GAMEDESIGN_MEM_001`. T17 migrated the second and T20
  the first, so both parameterisations now skip with a message saying so, and
  that class provides no coverage at all. The A9 derivation is still exercised
  by the synthetic suites, but the specification's own worked examples are no
  longer run against anything. Restoring them against a committed fixture
  instead of the live corpus is T21's, and is deliberately not done here.
  Full discovery: **829 OK, 3 skipped** - the third being the one this entry
  describes, alongside the game-design example and the pre-existing Windows
  symlink limitation.
- Seven of 81 claims still rest on a reasoning fixture alone, each recorded with
  why it cannot be executed: one needs a code example the card corpus does not
  contain (no software-engineering card carries a code fence), three need a
  corpus of task outputs graded against their own stated requirements that is
  not on this machine, and three need a second party - an independent runner, an
  independent grader, or separately-authored observation and diagnosis - which a
  single session cannot supply.
- `memory.py`'s L4 specimen-grade check reads `C++` as the grade `C+`. Three
  envelope statements were reworded to the legacy store's own "C plus plus"
  convention rather than widening the rule, which T20 may not do. Any future
  C++ Memory claim will hit it.

## 1.0.0-beta.129 - 2026-10-23

### Changed

- **The writing schema-3 migration is corrected after independent review: four
  propositions reinstated as survivors, three new claims, one claim's evidence
  and envelope repaired (T19 correction).** The review found the migration's
  mechanical apparatus sound and did not reopen the FREEZE, the decomposition,
  the second-reader pass, or the re-homes; it found four Canon-only verdicts
  wrong and one surviving claim internally inconsistent. The arithmetic below
  **supersedes the figures published in 1.0.0-beta.128**; everything beta.128
  recorded about the FREEZE, the 323-object baseline, the second-reader control,
  and the re-homes still holds.
- **Corrected accounting.** **37 legacy entries** decomposed into **100
  propositions**, which received **100 dispositions**, of which **42 survive**
  and name **23 distinct live claims** - twelve target ids are shared by more
  than one source proposition (merges) and no disposition is a split, so the
  surviving-disposition count and the claim count differ by 19 by design.
  Dispositions: CARRY 27, REWRITE 14, EXTRACT 1, REHOME 7, REJECT 51. Losses:
  **58** items (51 rejections, 7 re-homings), each signed individually with its
  own note; **zero** HOLDs and **zero** FLAGs. The **172** sentences of the
  thirty-seven entries' `observation`, `boundary`, and `diagnosis.hypothesis`
  are still each accounted exactly once - these corrections move dispositions,
  never proposition boundaries, so A9 is unchanged by construction. The store
  declares `memory_schema_version: 3` and `memory_version: 24`.
  `memory/writing/training_history.jsonl` remains byte-identical to its FREEZE
  hash at **76 events**.
- **Three reinstated claims, and why Canon does not own them.** Each was
  re-searched against the whole 323-object baseline, with the strongest
  candidates read in full and the absence confirmed by whole-package `grep`
  rather than by search rank. (1) `WRI_MEM_005#p1`/`#p2` merge into one claim
  about switching discourse form: the ranked owner,
  `PAT_expand_poetic_voice_by_borrowing_another_discourse`, is poetry-scoped in
  its normative text, triggers on lyric staleness rather than a changed
  narrative or cognitive job, and exits by subordinating the borrowed element to
  the poem's speaker rather than when its job is complete; the strongest prose
  candidate, `PAT_use_diaries_and_letters_as_active_story_documents`, is scoped
  to in-world documents and supplies no entry trigger. (2) `WRI_MEM_014#p3`
  becomes the density corrective: `DRILL_revise_clause_load_without_flattening_
  complexity` owns three of its four moves but no Canon object directs a reviser
  to make an abstraction concrete as a remedy for conceptual density - `grep`
  for `concretiz` returns **zero** hits across all 323 objects, and the nearest
  owner, `PAT_replace_abstractions_with_specific_sensory_images`, converts
  generalization into *sensory* detail, a descriptive remedy rather than a load
  remedy. (3) `WRI_MEM_019#p2` becomes the ordering claim: the owning card
  requires invented-language constraints to reach conduct or inference but says
  nothing about when, and its own timing bullet expressly permits meaning to be
  `supplied nearby`; the card that does state the ordering,
  `PAT_build_institutional_settings_as_rule_bound_social_worlds`, states it
  about institutional rules, not about a designed language, so joining the two
  would be the two-object synthesis this baseline forbids.
- **The over-retention claim's evidence and envelope now agree with its text.**
  The claim retains `WRI_MEM_023#p4`'s residue - that the retention returns
  during revision once control resumes - but was supported only by the comic
  pair from `WRI_MEM_037` while its envelope excluded *later drafts* and
  *non-comic forms*, which is where that half is demonstrated.
  `WRITING_EV_0046` joins the evidence as the analytical instance, the excluded
  regions are replaced by what is genuinely unshown (poetry, career writing, a
  second original story), and the first-draft-comic condition is replaced by the
  honest one: two unlike instances leave the cross-form generalization thin, so
  `confidence` stays `provisional`. The recurrence clause was preserved rather
  than dropped; dropping it would have been the cheaper repair.
- **One rejection's owner attribution corrected, outcome unchanged.**
  `WRI_MEM_024#p6`, the prohibition on optimizing against AI-authorship detector
  scores, now cites `DRILL_reverse_engineer_and_transform_a_writers_microstyle`
  instruction 12, which states the prohibition as a standing drill step, instead
  of a variant-scoped sentence in
  `PAT_replace_received_language_with_precise_distinctive_phrasing`. The legacy
  entry nominated that drill, so the rejection stands and
  `outside_nomination` remains false. With `WRI_MEM_014#p3` reinstated, the
  rejections owned outside the legacy nominations fall to **5 of 51**, and **36
  of the 51** verdicts rest on a variant.
- **Evidence admissibility re-proved explicitly, and the A-2 divergence count
  re-derived rather than assumed.** All **43** evidence references across the 23
  claims exist in the frozen History, are `valid`, are `performance`, are
  unquarantined, cite only the admissible set of each claim's own source
  entries, and no claim cites more than three; `t19_evidence_check.py`
  reproduces the proof and computes the default/selected comparison per claim.
  **2 of 23** claims diverge from the mechanical first-and-last default, against
  8 of 15 in T17 and 4 of 8 in T18. Both divergences are still merges spanning
  two legacy entries, and all **21** single-entry claims took the default
  unchanged - including the three reinstated ones. A-2 is not reopened and no
  specification change is proposed.
- **The loss report no longer presents a survivor as a loss.** The three
  migration reports were removed explicitly, re-derived from the corrected
  ledger, and re-signed: 58 items, 58 individual notes, no document-level
  approval and no bulk path. The four obsolete signoffs are gone from the live
  report, and the pre-correction signed report is retained beside the ledger
  under `superseded-pre-correction/` so the review trail survives.
- **Known issues left behind, unchanged by this correction.**
  `memory.py validate` still reports a legacy-entry tally that counts
  `.entries`, so the three v3 stores contribute 0 and the printed figure is 46 -
  software-engineering's entries alone; the behaviour is cosmetic and T21
  removes the remaining legacy branch. Re-running the gate against the live tree
  after cutover fails A9, correctly, because the legacy input no longer exists
  there; the post-cutover gate run used the frozen copy. software-engineering
  remains the last v1 store and is T20's, which stays blocked. The
  `SE_MEM_003`/`SE_MEM_016` contradiction pair and T18's owed
  `canon_workflow` hand-off for `DRILL_hold_one_head_type_across_expression_set`
  are both still carried forward untouched.


## 1.0.0-beta.128 - 2026-10-22

### Changed

- **The writing Skillset Memory store is migrated to schema 3: 37 legacy entries
  become 20 live claims (T19).** The third domain migration, and the only one
  whose input was a **v2** store. Accounting, with the units kept distinct
  because conflating them was T17's accounting defect: **37 legacy entries**
  decomposed into **100 propositions**, which received **100 dispositions**, of
  which **38 survive** and name **20 distinct live claims** - eleven target ids
  are shared by more than one source proposition (merges) and no disposition is
  a split, so the surviving-disposition count and the claim count differ by 18
  by design. Dispositions: CARRY 23, REWRITE 14, EXTRACT 1, REHOME 7,
  REJECT 55. Losses: 62 items (55 rejections, 7 re-homings), each signed
  individually with its own note; **zero** HOLDs and **zero** FLAGs. The
  **172** sentences of the thirty-seven entries' `observation`, `boundary`, and
  `diagnosis.hypothesis` are each accounted exactly once. The store declares
  `memory_schema_version: 3` and `memory_version: 23`; no v2 store remains
  anywhere. `memory/writing/training_history.jsonl` is untouched at **76
  events**, all valid, all `performance`, none quarantined.
- **The Canon-only baseline was the whole writing Canon from the first pass.**
  The baseline covers all **323** applicable Canon objects - 318 under
  `library/writing` and 5 under `library/metaskills` - counting one object as
  one markdown file whose basename begins `AP_`, `PAT_`, or `DRILL_`, excluding
  `INDEX.md` and `README.md` and not counting variants separately. `metaskills`
  inclusion was **re-proved for this domain** rather than carried over from
  T18: the writing release recipe's module closure is entirely internal, and
  `build_release.py` adds `metaskills` unconditionally and fails any build that
  omits it. That mattered - one survivor's verdict rests on a metaskills object,
  and excluding the package would have produced a false survivor. All 55
  rejections are `fails_canon_only_baseline`; **6 of them name an owning object
  the legacy entry never nominated**, and a nomination-bounded check would have
  admitted all six. Each rejection records its owning Canon object and the
  normative clause actually read; **38 of the 55 rest on a variant**, and in
  every case the owner recorded is the containing card. Search identified
  candidates and decided nothing; negative findings were confirmed by
  whole-package `grep` rather than by search rank.
- **Writing's Canon had already absorbed most of its Memory.** Three cards own
  23 of the 55 rejections, and `WRI_MEM_024` was rejected in all six of its
  propositions by a single card whose Do bullet and one variant state the
  entire entry - including its prohibition on treating detector output as a
  revision target. The 38 surviving propositions are of three kinds Canon
  structurally cannot hold: this skill's own demonstrated error profile, its
  capability calibration, and a small set of genuine craft gaps around reading
  a work whose representation is bad and matching evidence form to claim type.
- **All 37 entries were declared accretion narratives and every one received a
  genuinely independent blind second decomposition.** The blind input carried
  only the legacy semantic text and the numbered sentence inventory; it was
  sealed and the independent reader dispatched **before** the primary
  decomposition existed, so neither read could see the other. The reads
  returned 83 and 99 propositions; reconciliation adopted the second read in
  fifteen of the sixteen diverging entries and held the primary in one
  (`WRI_MEM_030`, where merging the prose-rendering limit would have
  under-decomposed). Four propositions were recovered only by the independent
  read, and **three of the twenty final claims depend materially on them**.
- **The four card candidates are re-homed to `canon_workflow` with every
  hand-off verified complete.** `WRI_MEM_031`, `032`, `033`, and `036` were
  checked present in `canon_workflow/writing/card_candidates.yaml` with their
  resolved destination ids **before** the legacy store was replaced, not
  assumed; the transcript is dated ahead of the removal. T11 owns the export
  and this ticket only verified and accounted it.
- **The four specialization profiles became `claim_class: reach`.** Each carries
  `delta.kinds` within `{posture, verification}`, and the four profiles yielded
  five reach claims because comic timing and comic editing are separately
  demonstrated capabilities. Every specimen title, named evaluator, and letter
  grade is stripped. All **seven** first-person legacy entries - `WRI_MEM_007`, `008`, `009`,
  `014`, `020`, `023`, `037` - were rewritten to model-neutral voice under
  `rewrite_reason: voice`, across 11 propositions and 7 target claims.
- **Evidence admissibility was proved explicitly against the frozen Training
  History** rather than left to the fail-open absent-History rule: all 37
  evidence references across the 20 claims exist, are `valid`, are
  `performance`, are unquarantined, and come only from the admissible cited set
  of each claim's own source entries. **2 of 20** claims diverge from the
  mechanical first-and-last default, against 8 of 15 in T17 and 4 of 8 in T18;
  both divergences are merges spanning two legacy entries, and all 18
  single-entry claims took the default unchanged. Recorded as an observation
  for the series - A-2 is not reopened and no specification change is proposed.


## 1.0.0-beta.127 - 2026-10-22

### Changed

- **The art Skillset Memory store is migrated to schema 3: 20 legacy entries
  become 8 live claims (T18).** The second domain migration, run with the T17
  correction applied from the start. Accounting, with the three units kept
  distinct because conflating them was T17's accounting defect: **20 legacy
  entries** decomposed into **72 propositions**, of which **17 surviving
  dispositions** name **8 distinct live claims** - six of those claims are
  merges, where more than one source proposition shares one target id, and no
  disposition is a split. Dispositions: CARRY 2, REWRITE 10, EXTRACT 5,
  REHOME 1, REJECT 54. The **144** sentences of the twenty entries'
  `observation`, `boundary`, and `diagnosis.hypothesis` are each accounted
  exactly once. The store declares `memory_schema_version: 3` and
  `memory_version: 23`; no v1 store remains for the domain. `memory/art/
  training_history.jsonl` is untouched at **80 events**.
- **The Canon-only baseline was the whole art Canon from the first pass, not the
  nominated links.** T17 failed its final review on exactly that defect, so T18
  built the baseline over all **645** Canon objects - 640 under `library/art`
  and 5 under `library/metaskills`, counting one object as one markdown file
  whose basename begins `AP_`, `PAT_`, or `DRILL_`, excluding `INDEX.md` and
  `README.md` and not counting variants separately. `metaskills` is in the
  baseline because every art release ships it, and excluding it would have
  produced two false survivors. Of the 54 rejections, **46** are
  `fails_canon_only_baseline`, and **20 of those name an owning card the legacy
  entry never nominated** - a nomination-driven check would have admitted all
  twenty. The remaining rejections are `not_portable` 5, `belongs_to_canon_
  workflow` 2, and `not_craft_scope` 1. Each rejection records its owning Canon
  object and the normative clause actually read; search identified candidates
  and decided nothing.
- **The eleven accretion entries received a genuinely independent blind second
  decomposition, and it changed the result.** An independent reader worked from
  the frozen `observation` / `boundary` / `hypothesis` text and §7.2 alone,
  launched before the first decomposition existed in any file so that
  independence ran in both directions. It was finer on all eleven entries - 51
  propositions against 35 - and its reading was adopted wholesale after
  reconciliation. Two of the eight surviving claims exist because of it: the
  insufficient-delta failure of a reduction pass, which the first reading had
  folded into its sibling leakage proposition, and the reach claim calibrating
  demonstrated against undemonstrated regions, which the first reading had
  labelled evidence recitation. The mark was earned by that reading, not written
  mechanically.
- **The single `resolved` entry and the single invalid event are both disposed
  of explicitly.** `ART_MEM_004` left current Memory with all six of its
  propositions rejected against the repaired Stage 4 Action Protocol, which now
  states each of them; no graveyard was created. No surviving claim cites
  `ART_EV_0003`, the one invalid event, and every cited event exists, is valid,
  is admissible, and belongs to its source entry's own cited set.
- **Four of the eight claims carry reviewer-selected evidence rather than the
  mechanical default**, which the specification permits. In every case the
  default was unrepresentative for the same structural reason: a tranche-rollup
  source or a merged claim makes "first and last cited event" a function of
  ordering or set union rather than of relevance. A-2 is not reopened and no
  specification change is proposed.
- **One Canon defect is re-homed rather than rejected, with the hand-off
  recorded as owed.** `DRILL_hold_one_head_type_across_expression_set` still
  requires observing facial tissue in a mirror, a premise that is not literally
  executable; the card was re-read to confirm the defect is current. Opening the
  Canon-quality item is left as an owner decision, since T18's blast radius is
  one memory store and one ledger.
- **T09's deferred test reversal (SR6) came due and is performed.**
  `tests/test_architecture.py::ReleaseMemoryTests::test_release_ships_the_memory_of_the_domains_it_bundles`
  reads the real art store rather than a fixture, and it asserted
  unconditionally that a release ships `memory/art/training_history.jsonl`.
  That was correct while the store was v1 and became false the moment T18
  migrated it, because a schema-3 store ships as a current-state projection.
  The assertion now follows the store's declared schema: for v3 it requires no
  shipped History and no `evidence` key on any staged claim, and the legacy
  branch remains for the pre-v3 stores until T21 deletes the legacy reader.
  T09 had already built the v3 behaviour and covered it against a fixture in
  `ReleaseV3MemoryTests`; only this real-store assertion was left inverted, by
  design, because inverting it before a real store was v3 would have broken the
  suite. A release built from the real art store was inspected as the ticket's
  completion evidence: one YAML per memory domain, no History, no `evidence`
  key, all eight claim ids byte-identical to the live store, and all four
  quality gates `passed`.
- **Known cosmetic reporting gap, left for T21.** `memory.py validate`'s summary
  line sums each store's `entries` key, so a schema-3 store contributes zero to
  that tally: the corpus now reports 83 entries, which is the legacy stores
  alone (software-engineering 46 plus writing 37). Every claim is validated -
  only the printed count excludes v3 - and T21 deletes the legacy branch that
  makes the line ambiguous. No acceptance criterion reads that number.
- **Stale README version statement repaired.** The versioning section had read
  "the current version is `1.0.0-beta.105`" since that release; it now tracks
  `VERSION` alongside the project-status line.

## 1.0.0-beta.126 - 2026-10-21

### Changed

- **The game-design Canon-only baseline is corrected to a whole-Canon audit,
  and the live store falls from 32 claims to 15 (T17 correction).** T17's final
  independent review failed the ticket on one defect: the baseline had been
  applied claim -> nominated Canon instead of claim -> whole Canon. The evidence
  file proved it - `canon-overlap-check.txt` printed, for each claim, only the
  cards that claim's own `canon` field already named. That is adequate for a
  rejection, which names its owning clause and can be re-checked, and worthless
  for an admission, because the owner that matters is usually a card the claim
  never nominated. The reviewer audited all 32 survivors against the whole card
  set and found 13 confirmed restatements, one borderline case, and four more to
  inspect. Nineteen propositions moved to REJECT. Final accounting: 33 legacy
  entries, 90 propositions, 197 sentences each covered exactly once, 15 live
  claims, dispositions CARRY 8 / REWRITE 6 / EXTRACT 2 / REHOME 4 / REJECT 70,
  with 69 of those rejections on the Canon-only baseline and one as
  `not_craft_scope`.
- **`duplicate_of` is now unused in this migration.** The last two such
  rejections, `GAMEDESIGN_MEM_001#p5` and `002#p4`, both named claims the
  correction rejected. Both were re-pointed at the Canon object that actually
  owns the lesson, so no rejection in the domain now defers to another Memory
  claim - every one names a card clause or a non-craft authority.
- **One fused claim was de-merged rather than rejected whole.**
  `GAMEDESIGN_MEM_001#p2` and `#p3` had been merged onto one claim, which forced
  one Canon-baseline result onto two assertions with different owners. `p2` - a
  shared randomizer is not a shared grammar - is the reuse-grammar Pattern's
  Don't outright. `p3` is not any card's: that the competence term of a pool is a
  separable axis, so the resolution can survive unchanged while what it measures
  changes. It survives as a new claim with its evidence narrowed to the one
  event that demonstrates it. Proposition boundaries did not move, so sentence
  coverage is untouched.
- **Four rejections go beyond the review's confirmed list, and two of its
  flagged claims were preserved.** `complexity_value`, `complexity_placement`,
  `operator_complexity_and_medium` and `campaign_hub_continuity` are Canon
  restatements - the operating-cost Pattern's Notes state the placement lesson
  with the claim's own rare-but-rich versus small-but-every-attack contrast, and
  the hub Pattern scored the highest single overlap in the audit at 0.568.
  `rule_removal_repair` and `force_visibility` were preserved on inspection:
  the first adds a confirmation criterion (operator and players independently
  rejecting the rule) that no card names, the second reconciles two cards that
  pull in opposite directions on withholding information.

### Notes

- The audit evidence is replaced, not patched. `WHOLE_CANON_ADMISSION_AUDIT.md`
  records a verdict and an owning clause for every one of the 32 claims, and
  `t17_canon_search.py` proves all 181 game-design cards were searched for every
  one and ranks the cards worth reading. The ranking is reading order only: no
  similarity threshold admits or rejects anything, and every classification was
  made by reading normative text. `canon-overlap-check.txt` is retired as
  `.SUPERSEDED`. Both artifacts stay untracked migration evidence; no runtime
  Canon-baseline engine was added.
- The borderline claim is decided explicitly. `local_operating_conditions` fails
  the baseline whole. Three of its four mechanisms are in the action-topology
  Pattern's Notes; the fourth, environment-specific rule behaviour, is one item
  in a four-item source list, carries no delta the card lacks, and has no
  surviving claim to qualify as an envelope condition. The decisive point is
  consistency: the same card had already rejected `018#p1`.
- A-2 remains a nonblocking specification finding, remeasured on the corrected
  set: 8 of the 15 surviving claims carry evidence the entry-level default would
  not have produced. Every surviving claim's evidence was re-checked as
  admissible and drawn from its own legacy entry.
- The independent Codex second-reader pass is unaffected and was not re-run.
  This correction changed dispositions and one claim-level merge, not any
  decomposition the second reading produced. Two propositions that reading
  recovered from silent folds, `002#p10` and `002#p11`, are now rejected as
  Canon restatements; recovering them was still right, because an accounted
  rejection is not the same outcome as a silent fold.
- Still T20's: the only same-scope contradiction pair in the corpus is
  `SE_MEM_003`/`SE_MEM_016` in software-engineering. None was invented here.

## 1.0.0-beta.125 - 2026-10-20

### Changed

- **`memory/game-design/skill_memory.yaml` is a schema-3 store: the first live
  Memory vNext semantic migration (T17).** Thirty-three legacy v1 entries were
  frozen, decomposed into 90 propositions with a complete 197-sentence coverage
  map, dispositioned one by one, and replaced by 32 authored v3 claims. Every
  claim carries a freshly generated `GD_MEM_` identity, a newly authored
  `delta`, an independently re-derived `confidence`, and an envelope
  restructured into `holds_in` / `not_shown_in` / `conditions`; no legacy id,
  sequence number, or migration record survives in the store. The legacy
  `type`, `scope_type`, `status`, `evidence_count`, `interventions`,
  `runtime_scope`, and `diagnosis` fields are gone with the schema, and the
  three legacy card-id scopes became topic scopes with the card moved to
  `canon`. `memory.py validate` now reports a mixed corpus - one v3 store and
  three legacy stores - and Training History is untouched at 28 events.
- **The dominant migration finding: 48 of this domain's 90 propositions were
  rejected on the Canon-only baseline, leaving 32 live claims out of 67 authored
  claim bodies.** (This bullet originally read "35 of the 67 claims authored from
  this domain were rejected on the Canon-only baseline", which labelled dropped
  claim bodies as Canon-baseline rejections and conflated bodies with
  propositions: of the 35 bodies dropped, 2 went as `duplicate_of` and 1 as
  `not_craft_scope`. Corrected in beta.126, which also corrects the baseline
  itself.) Each was compared against
  the normative text of every card that could own it, not only the cards the
  legacy entry nominated, and each rejection names the Pattern Rule, AP
  objective, or Drill instruction that already states both the proposition and
  its delta. Thirteen of the thirty-three legacy entries contribute no claim.
  The reason is structural rather than a defect in the legacy store:
  game-design's cards and its Memory were authored from the same source study,
  so an entry recording that a system behaved as its card predicts is a verdict
  on the card. This is R2.4's named failure mode found at scale, and it
  diverges sharply from R2.1's estimate of three card-verdict entries across
  the whole corpus - an owner-visible judgment the independent review can
  overturn item by item from the signed loss report.
- **The thirteen accretion entries' second-reader requirement is satisfied by
  an independent agent, and reconciling its findings changed the result.** The
  requirement was first executed by re-reading the same text myself, which this
  migration's own artifact recorded as insufficient. A separate agent then
  performed a blind decomposition from the frozen text, declared 66 independent
  propositions against the ledger's 53 for those entries, and returned
  *reconciliation required*: four under-decompositions, six substantive
  boundary disagreements, and five meanings absent from the proposition texts.
  Reconciling them added eight propositions, removed four claims, added one,
  and rewrote two. Four results are worth naming. One recovered proposition is
  now the only thing `GAMEDESIGN_MEM_006` contributes to Memory at all - the
  criterion separating a consolidation that also helps novices from one that
  serves experts only. Three fused propositions in the character-economy entry
  were joining assertions with *different* Canon owners, so one half of each
  escaped the baseline; split and tested, the drawback and lifecycle material
  is Canon's and the substitution-mastery axis is not. The production-probe
  entry had extended one sentence's "not table-playtested, so" over a second
  sentence's untested baseline, isolation, retention, and transfer, which table
  play would not have established either; that causal strengthening is removed.
  And two claims that named `AP_run_a_simulation_budget_audit` as their own
  Canon were restating it.
- **`tests/test_memory_migration.py` handles a mixed-schema live corpus.** The
  Memory-tree firewall test now proves the migrator writes nothing under
  `memory/` on the refusal path a schema-3 store takes, as well as on the
  success path a legacy store takes, and the specification-example suite skips
  a domain whose legacy example entry its own migration has consumed. Neither
  assertion is weakened; T21 removes the suite when the last domain migrates.

### Notes

- A-2 is answered on the first domain migrated, as R2.5 §11 asks, with the
  recommendation to **change** the representative-evidence default: it is
  specified per legacy entry but every claim comes from a proposition, so on a
  split - the normal case - it has no defined meaning, and 18 of the 32
  surviving claims carry evidence it would not have produced. The finding and
  its two concrete constraints are in the migration task's workspace.
- T17 introduced no `contradicts` pair. The one known same-scope pair in the
  corpus is `SE_MEM_003`/`SE_MEM_016`, in software-engineering, so the
  disputed-pair writer question stays open for T20 rather than being forced
  here. The T17 ticket's rationale attributes that pair to game-design; it does
  not hold, and the ticket's third acceptance criterion is inapplicable rather
  than satisfied.
- One weakness is carried forward rather than repaired here. The Canon-only
  baseline's *rejections* each name an owning clause and can be audited; its
  *admissions* cannot be shown to have been tested against the cards that might
  own them, because the overlap check was driven by each claim's own `canon`
  list. Four of the five restatements found during reconciliation were found by
  reading a card the claim had not nominated. T18-T20 should drive the baseline
  from the domain's whole card set. **Carrying this forward instead of resolving
  it is what failed T17's final independent review; beta.126 resolves it.**

## 1.0.0-beta.124 - 2026-10-20

### Added

- **The migration ledger now produces the three R2.5 §7.5 reports, and the
  loss report cannot be approved in bulk — it is signed item by item, and
  `gate` is the single VERIFY-step entry point (criterion 45).**
  `migrate_memory_v3.py report --domain <d>` derives three artifacts from the
  ledger's recorded dispositions, deterministically and never from a second
  hand-maintained record: **survival** (every CARRY, REWRITE, SPLIT, CONDENSE,
  and EXTRACT proposition and the target claim(s) it survives as, with a
  SPLIT's full target list and a merge's shared target shown exactly as
  recorded), **loss** (every REJECT with its reason kind, prose reason, and
  any `duplicate_of` obligation; every REHOME with its destination and
  pointer-or-hand-off; and every proposition shed inside a CONDENSE with its
  `shed_reason` and the condensation it was shed from — the anti-silent-drop
  report), and **re-homing** (every REHOME and EXTRACT with destination,
  residue targets where they exist, and a complete-or-owed hand-off status
  derived from the ledger's own pointer-vs-hand-off vocabulary). The loss
  report is the signoff artifact: each item carries its own `signed_off`
  field and reviewer note, the schema has no document-level approval key, and
  regeneration refuses while existing reports would be overwritten so a
  reviewer's signoffs are never silently destroyed. Reports land in the
  task's purpose directory beside the ledger, never under `memory/`.
- **`migrate_memory_v3.py gate --domain <d> --store <path>` is the VERIFY
  gate: A1–A10 re-run, zero HOLDs, the candidate through the real v3
  validator, every FLAG reviewed, every loss item signed.**
  The gate re-runs the existing accounting checker rather than forking it —
  A2 source drift and a remaining HOLD refuse exactly as under `account`,
  never warn — and requires the loss artifact to equal the ledger's own loss
  set in both directions: a missing row, a row naming something that is not a
  loss, a duplicate row, a reason edited after signing, a `signed_off` that
  is not the literal `true`, or an empty reviewer note each refuse. The
  candidate store goes through `memory.py`'s actual v3 validator (ERRORs
  refuse; a History file beside the candidate resolves evidence, its absence
  does not), and every FLAG must be cleared or individually accepted with a
  note in a `review-<domain>.yaml` artifact beside the ledger — a stale
  acknowledgment refuses, and acceptance never mutates Memory. There is no
  bulk-approval field, flag, or environment variable, asserted by grep and by
  structural refusal; the gate writes nothing and decides nothing semantic —
  whether a loss was right stays review judgment.

## 1.0.0-beta.123 - 2026-10-19

### Added

- **A9 now proves sentence coverage: every source sentence of a decomposed
  entry is attributed exactly once, or the ledger fails (R2.5 §7.2, §7.5,
  criterion 44a).**
  Each decomposition carries a `sentence_map` — one record per source sentence
  number, attributing it to at least one proposition id recorded in that
  entry's decomposition or to a closed non-propositional reason
  (`evidence_recitation`, `episode_narrative`, `restatement`,
  `environment_context`, `canon_restatement`). `account` re-derives each
  frozen entry's inventory from the frozen bytes — `observation`, `boundary`,
  and `diagnosis.hypothesis` concatenated in that order (§7.4 step 1, no
  per-field slicing) and split with `validate.py`'s `SENTENCE_RE` — so A9,
  reported as delegated since beta.122, is now the real check and names every
  failure: a sentence with no row, a sentence counted twice, a row outside the
  inventory, or a reference to a proposition id absent from that entry's
  decomposition. The ledger also declares which entries are accretion
  narratives (`accretion_entries`), and A9 checks each declared entry's
  decomposition record for the presence-only `second_reader: true` mark, in
  both directions — the mark's presence, never the reading. Coverage, never
  comprehension: the checker does not read what a sentence means and never
  judges whether an attribution is honest.
- **`migrate_memory_v3.py sentences --domain <d> --entry <id>` emits the
  numbered sentence inventory of one legacy entry — A9's source text.**
  Emission only: nothing is attributed, decomposed, classified, or written,
  and the subcommand has no ledger flag, so it cannot read or touch a ledger.
  Segmentation is the repository's one sentence splitter, imported rather
  than copied, so unchanged bytes yield an identical list on every run.

## 1.0.0-beta.122 - 2026-10-19

### Added

- **The migration ledger now carries a schema, and `account` checks recorded
  judgments against all ten completeness rules (R2.5 §7.2–§7.5).
  `migrate_memory_v3.py account --domain <d> --ledger-dir <dir> --store <path>`
  first validates the ledger's structure — required blocks, the closed
  disposition class vocabulary (CARRY, REWRITE, SPLIT, CONDENSE, EXTRACT,
  REHOME, REJECT, plus the transient HOLD), the closed rewrite-reason,
  rejection-reason-kind, and destination-authority vocabularies, and the
  `<legacy-entry-id>#p<n>` proposition identity shape — refusing a malformed
  artifact before any check runs. It then runs A1–A10: every legacy entry
  decomposed exactly once; the frozen hashes still matching (A2, reusing
  T13's mechanics); every proposition dispositioned exactly once, including
  CONDENSE sheds as explicit per-proposition accounting; every disposition
  carrying its class's obligation; every target claim existing in the
  candidate store; every store claim named by at least one disposition; zero
  HOLDs; counts reported with the merge difference stated rather than an
  equality asserted; and every target a well-formed vNext id that equals no
  legacy entry id or proposition id. A9 is reported as delegated to T15.
  Every failure names its check. The checker never assigns, proposes, or
  suggests a disposition and never judges semantic fidelity — completeness
  and referential integrity only — and it writes nothing, to `memory/` or
  anywhere else. One-time tooling, deleted by T21 with the legacy input
  reader.

## 1.0.0-beta.121 - 2026-10-19

### Added

- **Migration FREEZE records a legacy Memory store exactly, or refuses it
  (R2.5 §7.4 step 0).** `migrate_memory_v3.py freeze --domain <d>` runs the
  existing Memory validator against a v1/v2 store — the same dispatch
  `memory.py validate` uses — and on success writes a one-time
  `ledger-<domain>.yaml` into the task's workspace purpose directory: the
  store's `memory_schema_version`, `memory_version`, entry count, a sha256 of
  each entry's exact serialized bytes, and the admissible event id set (valid +
  performance + not quarantined, the CRQ rule mirrored rather than imported).
  `verify-hashes` re-checks every recorded hash and the entry id set (check
  A2), so an entry edited, removed, or added after FREEZE fails loudly. The
  tool refuses an invalid store without emitting a ledger, refuses a schema-3
  store, refuses to overwrite an existing ledger, and never writes under
  `memory/`: legacy stores stay read-only migration inputs until their own
  domain migration is signed off. It decomposes nothing, classifies nothing,
  authors no vNext claim, and computes no confidence — judgment stays with
  models and humans. One-time tooling, deleted by T21 with the legacy input
  reader.

## 1.0.0-beta.120 - 2026-10-19

### Changed

- **A release stages a schema-3 Memory store as a current-state projection
  (R2.5 §8.5).** `build_release.py` reads a v3 `skill_memory.yaml`, drops every
  claim-level `evidence` key, and ships only that file — no
  `training_history.jsonl` — for each owned domain. Every claim id and every
  other key carries through unchanged; the source store is read and never
  rewritten. `check` rejects a v3 store shipped with History beside it or with
  an `evidence` key still present, and the SKILL.md memory section says the
  copy is a projection when no History ships. Stores of any older schema still
  ship whole, History included, until the legacy reader is deleted. Project
  snapshots are unaffected: they continue to round-trip the full writable
  store, and their import gate validates those shipped bytes.

## 1.0.0-beta.119 - 2026-10-18

### Added

- **`memory.py review` has a schema-3 surface, and it reports rather than
  repairs.** A v3 store is now reviewed by its own path: a past-due
  `revalidate_after`, the FLAG rules (C2 fusion word count, C5 three-kind
  delta, L5 host-local prose, and I2 an unresolved `canon` id), every valid
  disputed pair, and the informational uncited-events line. Findings are read
  only - review writes no file, leaves `memory_version` alone, appends no
  History event, and keeps no receipt, sidecar, cache, or acknowledgement that
  a finding was seen. A finding is a property of current state, so it comes
  back on every run until an authorised write changes that state.
- **A valid disputed pair is a review item, listed once.** Both claims stay
  present and retrievable. Review performs no demotion, no merge, no erasure,
  no confidence change, no winner selection, and no retirement: which side
  wins is a human judgment the tool does not make or record. The stale R2.5
  wording that `review` reports *asymmetric* `contradicts` is superseded -
  after beta.118 asymmetry is an ERROR, so a well-formed pair is the only
  contradiction shape left to surface.

### Changed

- **Review and validation are two channels, and review never softens the
  other.** A structurally invalid store is reported under `ERROR:` with its
  rule id and exits non-zero, and its findings are withheld rather than
  restated as softer concerns: a malformed contradiction - one-sided, missing
  its target, or naming more than one counterpart - stays an error. No ERROR
  rule was downgraded to a flag to let review continue.
- **Age triggers a listing and nothing else (F2).** A past-due claim is not
  suppressed, not rank-penalised, and not relabelled; `last_verified` and
  `revalidate_after` are untouched. A store whose every claim is past due
  retrieves identically to one that is not. `STALE_DAYS` no longer reaches the
  v3 path - the per-claim date replaced the repository-wide constant - and the
  legacy `confidence strong on N event(s)` heuristic was not ported, so no v3
  review output computes, suggests, promotes, or demotes a confidence, or
  prints one at all (F1, SR4).
- **Unresolved `canon` ids are conditional on the library.** I2 is reported
  only when a `library/` root exists; with none, the same store stays valid and
  unflagged, because library absence is a missing input and not Memory
  corruption. Review reports only what failed to resolve and never enumerates
  the links that did - listing them would be Memory offering a Canon menu, and
  Canon is selected before Memory is read.

### Known issues

- A valid disputed pair cannot be resolved through the ordinary one-claim
  `retire`: removing either member leaves the survivor with an I6-asymmetric
  link. I6 is not weakened and no atomic pair-resolution operation was
  invented; the gap is recorded for a later decision.
- A schema-invalid mapping-shaped `contradicts` can still crash `query`, which
  slices the value before checking its list shape. Found during the beta.118
  review, bounded, and left for a separate maintenance decision.

## 1.0.0-beta.118 - 2026-10-18

### Fixed

- **A contradiction is a disputed pair, and `contradicts` now carries exactly
  one claim id (S9).** R2.5 §4.8 defines the relation as a pair and names the
  other side a *counterpart*, singular, but never stated the cardinality as a
  rule. The gap was latent until T07 built co-return on top of it: retrieval
  expanded the whole contradiction-connected component, so a validator-accepted
  symmetric chain of 10, 100 or 1,000 claims came back entire from
  `--limit 1` - bounded by the store rather than by the request, which is the
  store dump R2.5 §9.2 forbids. Absent `contradicts` stays valid and one member
  stays valid; more than one is now an ERROR. With I6's symmetry and
  no-self-reference, every valid contradiction component is exactly two claims,
  so chains and contradiction graphs are rejected at the schema.
- **Co-return is one hop to one counterpart and never recursive.** Retrieval
  attaches the single direct counterpart of each ranked claim; the recursive
  component walk is deleted. Expansion is at most one counterpart per ranked
  claim, so what a query returns is bounded by the request. The bound is a
  property of retrieval rather than of the store it reads: retrieval takes the
  one counterpart a valid claim has, so a malformed file cannot make a query
  unbounded either. No traversal or component budget was introduced - a budget
  would have made the bound a tuning number instead of a structural fact.

### Unchanged

- Every other accepted T07 behavior: the rank tuple and its order, Canon
  authority and the printing of no card id, opaque ids, `revalidate_after`
  changing nothing, empty and missing query behavior, exactly one receipt, and
  the legacy `score_entry` / `query_store` path. The counterpart still does not
  consume the caller's limit, still returns with the ranked member, and still
  produces the same pair receipt segment. The live corpus is legacy and
  byte-untouched.

### Documentation

- `PASS/docs/MEMORY_SCHEMA.md` states the pair cardinality in the claim schema,
  in S9, and in a new section that says why it is a bound and not a style
  rule. `memory/README.md` and the `query` help say the counterpart is one and
  that co-return never walks a chain. The R2.5 design artifacts under
  `workspace/handoffs/` are left as written: the underspecification they
  contain is part of how this defect happened.

### Tests

- `V3ClaimInvariants::test_a_contradiction_carries_exactly_one_counterpart`
  rejects a claim naming two targets while both name it back - a store I6
  accepts, so the pair cap is demonstrably what catches a graph.
- `V3ReferentialIntegrity::test_a_three_claim_contradiction_chain_is_structurally_rejected`
  and `::test_a_contradiction_triangle_is_structurally_rejected` reject both
  three-claim components, chain and cycle, and confirm the two-claim pair still
  validates.
- `V3Retrieval::test_a_limit_of_one_cannot_expand_into_a_contradiction_chain`
  is the defect's regression, at review's 10, 100 and 1,000;
  `::test_expansion_is_bounded_by_the_request_at_every_limit` holds the general
  bound; `::test_a_store_that_breaks_the_pair_rule_still_cannot_dump` holds it
  over a store the validator refuses. Each was mutation-checked: restoring the
  component walk, dropping the one-counterpart take, and removing the S9
  cardinality branch each made them fail before being reverted.
- `pop` leaves the retrieval AST allowlist with the frontier queue it existed
  for.

## 1.0.0-beta.117 - 2026-10-18

### Added

- Added the schema-3 retrieval path to `PASS/tools/memory.py`:
  `score_claim(claim, scope, canon_ids, cues)`, `query_v3_store` and
  `print_v3_claim`. `query` now routes each store by its own
  `memory_schema_version`, so a corpus part way through migration answers one
  request (R2.5 §9.2, criteria 29-33, 7l, 13, 19).
- `query` takes `--scope` (one topic slug, matched exactly) and `--canon`
  (comma-separated Canon object ids, matched exactly). `--scope-id` remains as
  the legacy spelling of `--scope` and is deleted with the rest of the legacy
  reader.

### Changed

- **Ranking is a tuple compared left to right, not a weighted score.** Exact
  `scope`, then exact `canon` id, then cue and claim substrings, then
  `confidence`. A weight would make "confidence ranks last" an arithmetic
  accident that enough cue hits could overturn; the tuple makes it structural.
  Ranking reads `confidence` and never writes it, and a query leaves the store
  byte-identical (F3).
- **`canon` ids are matched against what the caller already pinned.** Canon
  selection runs before Memory retrieval and the ids come in from the caller.
  No path enumerates a claim's `canon` links to propose, rank or discover a
  Canon object, and the query output deliberately prints no card id: returning
  the links of everything retrieved would hand back a list of Canon objects
  that Memory assembled. A `reach` claim carrying a `canon` link is therefore
  retrievable by it and still cannot route (R2.5 §9.2, §4.4).
- **A contradicted claim never comes back alone.** A returned claim's
  `contradicts` counterparts are returned with it, following the whole
  contradiction component rather than one hop, and they are not charged
  against the caller's limit. The single receipt names them in their own
  segment so a counterpart can never be read as a claim that spent a slot
  (R2.5 §4.8).
- **An empty scope with no cues and no canon ids is reported as not a
  retrieval strategy** and answered with nothing. Returning the first N claims
  would be a store dump wearing a limit.
- A `--canon` request against a store below schema 3 prints a note saying it
  could not be used to match, rather than dropping the filter silently - a
  dropped filter reads as a filter that matched nothing.
- **`query` fails open.** A missing memory root or a missing domain now exits 0
  with a `note:` line and an honest empty receipt instead of exiting 1, because
  nothing in PASS may stop because Memory is absent. A store that is present
  but unreadable still fails loudly: that is a broken file, not an absent one.
- Claims of equal rank keep the order the file gives them. Sorting by id is
  exactly what an opaque key forbids, and the file's order is the only other
  deterministic order available.
- `revalidate_after` being past changes nothing about retrieval: no
  suppression, no penalty, no reordering. T08 owns review-time visibility.
- `memory/README.md` now states the retrieval contract and shows the v3 query
  surface.

### Unchanged

- The legacy `score_entry` / `query_store` path and its output are untouched
  and keep serving v1/v2 stores until T21 deletes them. The live corpus is
  still legacy and is byte-untouched by this commit.

### Tests

- `tests/test_memory.py::RetrievalContract` is re-pointed at schema 3;
  `test_resolved_entries_stop_being_retrieved` becomes
  `test_a_retired_claim_is_absent_from_the_store`, because v3 has no
  retrievability status - retirement removes the claim (R2.5 §1.4).
- New `V3Retrieval` covers bounding across every request shape and limit,
  scope and canon outranking a cue match, claim-text substring matching, a
  reach claim found by its Canon id, contradiction co-return and its
  non-consumption of the limit, `revalidate_after` changing nothing,
  confidence ranking last without a write, id opacity from the outside,
  missing root / missing domain / empty store, exactly one receipt, and the
  empty-request report.
- New `V3RetrievalSurface` reads criteria 7l, 9 and F3 off the syntax tree: an
  allowlist of every name and method the ranking path may reach for, a check
  that retrieval stores into nothing it was given, and the exact set of
  functions in the tool that read a claim's `canon` key, each with the reason
  it is allowed to.

## 1.0.0-beta.116 - 2026-10-18

### Added

- Added `link-evidence` to `PASS/tools/memory.py`:
  `link_evidence(domain_dir, claim_id, event_ids, replace=False)` makes one to
  three admissible events a claim's complete `evidence`, sets `last_verified`
  to today, and runs through the existing `change_claims` path — whole-store
  validation, per-domain lock, atomic replace, `memory_version` +1, readback
  confirmation, and a refusal that leaves the file byte-identical. A fourth
  id, an empty list, or a repeated id is refused at the write seam; S9 holds
  the same cap of three for any other path (R2.5 §3.5, §8.3, criterion 15).

### Changed

- **Evidence admissibility at the link seam is now the shared helper T03
  owns.** `link_evidence` calls `evidence_admissibility_problem` instead of
  a private copy of the rules, so unknown, invalid, correction, quarantined and
  non-performance events are refused with exactly the message `validate` would
  raise inside the store. A store with no `training_history.jsonl` refuses
  rather than linking evidence it cannot verify. Admissibility semantics are
  unchanged.
- `--events` stays the claim's complete evidence after the call. Dropping an id
  the claim already cites is refused without `--replace`; with `--replace` the
  write succeeds and the dropped ids are reported on stdout instead of being
  lost silently.
- The uncited-events line from `review` is relabelled informational (R2.5
  §8.4): it states that it is not a backlog and not a measure of support, and
  it now counts citations from v3 claims' `evidence` alongside legacy entries'
  `evidence_events`. Under a cap of three the number is a view of History
  nothing has linked yet, not a queue to drain.
- `memory/README.md` and the pass-authoring command block —
  `.claude/skills/pass-authoring/SKILL.md` and its `.agents` mirror — now name
  `link-evidence`.

### Removed

- **Removed `compact`** from the tool, the help, and the source, with it
  `compact_link`, `_compact_link`, `cmd_compact`, and the report mode that
  called uncited events "awaiting consolidation". `link-evidence` replaces it.
- No write path ever writes `evidence_count`, and `link_evidence` never reads,
  writes, or prints a `confidence` (F1): representative evidence is
  illustrative, never a measure, and the linked ids never influence any
  ranking, note, or output ordering.

### Tests

- New `tests/test_memory.py::V3LinkEvidence`: three ids accepted, a fourth
  refused; invalid, correction and quarantined events refused through the
  shared helper; a drop refused without `--replace` and reported with it; no
  `evidence_count` in the store and none assigned on the write path (checked on
  the syntax tree); no confidence mutated or printed; `compact` absent from
  `--help` and the source; and the uncited line asserting "informational",
  "not a backlog" and "not a measure". The six legacy-fixture `compact` tests
  re-point here as `link-evidence` tests: linking is schema-3 only since T05,
  so they cannot stay on v1 fixtures.
- `V3WriteConfidence.WRITE_FUNCTIONS` now covers `link_evidence`;
  `test_a_legacy_store_is_not_writable` and
  `test_a_write_needs_exactly_one_domain` cover the new command.

## 1.0.0-beta.115 - 2026-10-18

### Added

- Added the Skillset Memory v3 writer to `PASS/tools/memory.py`: `add_claim`,
  `update_claim` and `retire_claim`, reached from the new top-level `add`,
  `update`, `retire` and `show` subcommands. `add` generates the claim's id
  itself (R2.5 §3.4) and refuses a caller-supplied one; `update` can reach every
  field except `id`; `retire` requires `--reason` and **physically removes** the
  claim, because currentness is presence (§1.4). The reason is operator-facing at
  the moment of the write and is persisted nowhere — no tombstone, no retired-id
  list, no lineage field, no sidecar, no History event.
- Added the §9.4 admission prompt. Before every `add`, and before any `update`
  touching `claim` or `delta`, the writer prints the R2.4 admission question and
  the Canon-only baseline verbatim, including when the write is then refused. It
  is a prompt, not a gate: the tool validates `delta`'s shape and never judges
  whether the delta is real, and it never reads from stdin.

### Changed

- **Writing Skillset Memory is now schema-3 only** (R2.5 §9.1). A v1 or v2 store
  is still read and validated through the T04 dispatch, but a write against one
  is refused naming the schema; the way to change a legacy store is to migrate
  its domain. The whole-store validation, per-domain lock, atomic replace,
  `memory_version` +1 and readback confirmation are carried over unchanged, now
  keyed on `claims` and checked against the v3 validator.
- Generalized `spliced_store` over the store's collection key, so untouched v3
  claims keep their bytes and line endings exactly as untouched legacy entries
  did. R2.0 calls byte-splicing implementation rather than contract; it survives
  because one key name was its whole cost.
- Rewrote the write-discipline statements in `memory/README.md` and the memory
  command block in `.claude/skills/pass-authoring/SKILL.md` (and its `.agents`
  mirror) for v3: generated ids, retirement as removal with a mandatory
  operator-facing reason, replacement as `retire` then `add`, and no computed or
  inherited confidence.

### Removed

- **Deleted the sequential claim allocator** `next_entry_id` rather than porting
  it. It derived the next number from the highest *surviving* entry, so the first
  `add` after a retirement reissued the retired id. Training History keeps its
  own sequence: `next_event_id` is untouched, because events are append-only and
  nothing removes one (§8.4).
- **Removed `supersede`** from the tool and its help, with `add_entry`,
  `update_entry`, `supersede_entry`, `change_entries`, `ordered_entry`,
  `ENTRY_KEY_ORDER`, `find_entry` and the `entry` subcommand group. A replacement
  is `retire` then `add`, with a fresh id and an independently re-derived
  `confidence`; no write path computes, suggests, copies or auto-promotes a
  confidence value (F1–F4), which `tests/test_memory.py` now locks at the syntax
  tree as well as end to end.

### Tests

- Replaced `EntryCommands` with `V3WriteIdentity`, `V3Retirement`,
  `V3WriteConfidence`, `V3Admission`, `V3WriteSafety` and `V3WriterSurface`
  against temporary v3 stores, the live corpus being untouched. The reversals are
  deliberate and named: `test_there_is_no_delete` became
  `test_retirement_removes_the_claim_and_requires_a_reason`, the two supersede
  tests became `test_replacement_is_retire_then_add_with_a_fresh_id`, and
  `test_the_legacy_allocator_is_still_present_for_the_legacy_tree` became
  `test_the_sequential_claim_allocator_is_gone`.
- `test_retiring_a_contradiction_target_is_refused` records a found gap rather
  than working around it: §4.8 forbids automatic erasure of a contradiction
  marker, so a contradicted pair can be neither retired nor unlinked one claim at
  a time. Resolving a pair needs a single write touching both claims, which is
  not on the §8.3 operation surface.

## 1.0.0-beta.114 - 2026-10-18

### Added

- Added schema-version dispatch to Skillset Memory (`PASS/tools/memory.py`):
  `validate_contents` now returns `(errors, flags)` and routes each store's
  claim side by `memory_schema_version` — schema 3 to `validate_v3_contents`,
  schemas 1 and 2 to the new `PASS/tools/memory_legacy_input.py`, anything
  else to the existing unknown-version error — while Training History
  validation (event shape, duplicate event ids, correction ordering) runs
  unchanged for every version, because History is not versioned (R2.5 §8.4).
  A mixed-state corpus of v1/v2 and v3 stores now validates in one `validate`
  run, which also prints each store's declared schema version and any review
  FLAGs (a flags-only result still exits 0).
- Added `PASS/tools/memory_legacy_input.py`, the isolated v1/v2
  migration-input reader: the legacy claim vocabularies and `validate_entry`
  moved there verbatim. Its docstring binds it to deletion by ticket T21 and
  forbids any runtime path from growing a dependency on it, and
  `tests/test_memory.py::SchemaDispatch` enforces that the dispatch in
  `memory.py` is its only importer. A v3 store beside an absent
  `training_history.jsonl` keeps its I5 semantics through `validate_store`:
  absence is not corruption, and the file is not reported missing.

### Changed

- Extracted one shared evidence-admissibility implementation
  (`evidence_admissibility_problem`, field-parameterized) called by both the
  legacy `evidence_events` path and the v3 `evidence` path, with quarantine
  derived by the single `quarantined_event_ids` helper, so the invalid-run
  invariant cannot drift between the two claim sides. Legacy messages read
  exactly as before; v3 messages keep their `(I4)` rule tags.

## 1.0.0-beta.113 - 2026-10-18

### Added

- Added v3 referential integrity to Skillset Memory (`PASS/tools/memory.py`):
  `validate_v3_references` implements the R2.5 §4.6 rules I1–I6. Canon shape
  (I1) and evidence-id shape (I3) are checked always; canon resolves against
  the claim's own package plus `metaskills` only when a `library/` root is
  supplied and present, and a reference that does not resolve is a FLAG for
  review rather than an ERROR (I2), so Memory validity never depends on
  library state. Evidence members resolve against `training_history.jsonl`
  only when it is present, reusing the legacy invalid / correction /
  quarantine admissibility semantics unchanged (I4); with History absent they
  are not resolved and the store stays valid (I5). `contradicts` targets must
  exist in the same store, be symmetric, and never self-reference (I6).
  `validate_v3_store` now accepts an optional library root and loads History
  only when the file exists.
- Added the `tests/test_memory.py` `V3ReferentialIntegrity` suite (21 tests)
  and extended `Portability` with two criterion-28a tests: a v3 store
  validates in a bare directory containing nothing but
  `memory/<domain>/skill_memory.yaml` (with or without a `.git` directory
  beside it), and `PASS/tools/memory.py` never names, imports, or runs a
  version-control command.

### Changed

- Updated `PASS/docs/MEMORY_SCHEMA.md` §10 with the I1–I6 rule-table rows and
  the conditional-resolution design: shape checked always, evidence resolved
  only against a present History, canon only against a present Library root.

## 1.0.0-beta.112 - 2026-10-17

### Added

- Added Skillset Memory schema v3 structural validation (`PASS/tools/memory.py`):
  `validate_v3_contents` / `validate_v3_store` implement the R2.5 claim-store
  contract as a pure function beside the untouched legacy validator — store
  shape and required fields (S1–S10), claim prose and fusion smells (C1–C6),
  envelope invariants (E1–E2), the reach posture invariant (R1), and the
  retired-vocabulary/leakage gates (L1–L5) — with errors and flags on separate
  channels so a flags-only result stays exit-zero. Runtime dispatch is not
  wired; the four live v1/v2 stores keep the legacy validator unchanged, and a
  v3 store has its own `CLAIM_FORBIDDEN_KEYS` list (provenance is required
  there, rejected in v1/v2).
- Added `PASS/docs/MEMORY_SCHEMA.md` §10 documenting the v3 store shape, the
  claim schema, the closed vocabularies, the full rule table with ERROR/FLAG
  channels, and the semantic checks v3 validation deliberately cannot make.
- Added the `tests/test_memory.py` v3 suite (45 tests): store shape, closed
  vocabularies, required fields, word caps, accretion connectives, envelope
  sentinels, reach/delta closure, cross-store id collision, legacy-key
  rejection, the identity/leakage gates, the spec's boundary cases, and the
  three verbatim §6 specification examples.

## 1.0.0-beta.111 - 2026-10-17

### Added

- Added Stage Contract v1 (`PASS/runtime/stage_contract.py`): one closed,
  model-facing structural response for Preflight, PASS 1, CHECKPOINT, PASS 2,
  PASS 3 and both closure stages, so every supported model returns the same
  artifact. Free-form model cognition, a closed stage output contract, then
  deterministic host validation and rendering. Model reasoning and semantic
  conclusions remain unconstrained.
- Added `python PASS/pass.py schema [--stage <stage>] [--enums]`, the
  authoritative JSON Schema and declared vocabularies, generated from the same
  declarations the templates and the validator use.
- Added `PASS/docs/STAGE_CONTRACT.md` with the ownership split, the envelope, the
  failure codes and worked artifacts for all four stages plus a rendered Pattern,
  AP and Drill.
- Added `tests/test_stage_contract.py`: cross-model conformance (structure,
  schema, enums and host-written files must match while semantics may differ),
  host path ownership, write-nothing-on-invalid, stale-token refusal, the bounded
  correction attempt and fail-close, and preflight schema independence.

### Changed

- Stage responses are now the envelope `{"action_id": ..., "payload": ...}`. The
  model echoes one opaque host-issued token that binds the bound source, stage,
  unit index, unit and controller state, and states no other identity. This
  replaces the `schema_version` and `unit_id` echoes and is strictly stronger: a
  response produced for another unit, stage or superseded state is refused with
  `stale_action_id`.
- Drafted cards cross the boundary as structured objects rather than files. The
  model supplies `object_id`, `object_type`, `library_path`, `name`, frontmatter
  and an object-type-specific body; the host derives the path, renders every
  heading, heading order, IF/THEN/ELSE label, list marker, indent and blank line,
  and writes the file only after the whole response validates. The audit behind
  this verified it is lossless: across all 2,388 library cards `object_id` equals
  the filename stem and `library_path` equals the directory, with no exceptions.
- Non-card staged items are typed `artifacts` -- an owned release recipe, a
  `MODULE.yaml`, or an asset -- whose paths the host derives from declared
  identity. A model no longer composes any path string.
- Removed `reviewed_sha256`, `working_drafts`, `changes`, `schema_version`,
  `unit_id` and `mode` from the model-facing payloads. The host already owned
  every one of them and now writes them itself; PASS 3 attests with
  `card_only_review` and `checks`, and the host computes the staged digests before
  and after validation as it already did.
- Retired `overlap_object_ids` from the PASS 1 payload, which had no downstream
  consumer. The reasoning obligation is unchanged and PASS 2's buckets still carry
  the reconciliation. The identically named *preflight unit* field is kept: it is
  validated against the library, printed in the human-facing preflight packet and
  counted in the verification summary.
- `template` now prints the envelope with a payload skeleton generated from the
  schema and seeded with the identifiers the host already owns, eliminating the
  split between SHOUTING preflight placeholders and empty-value workflow
  templates. No value's status is ambiguous any more.

### Fixed

- Fixed the unbounded retry hole: a malformed stage response is refused before
  anything is written and recorded as a machine-readable
  `controller/stage-rejection.json` with a closed failure-code vocabulary. The
  same pending action gets exactly one correction attempt; a second malformed
  response fails the stage closed, preserves the last completed boundary, and
  makes unattended mode return `blocked_human_required` instead of reissuing the
  same action forever. Infrastructure failures and semantic outcomes --
  `approval_required`, an honest `false` check, a legitimate empty result -- are
  not contract failures and consume no attempt.
- Corrected two enum defects found while building the contract: `card_potential`
  was missing `mixed`, which the synthetic closure unit uses, and `text_quality`
  is free text upstream rather than an enum. A test now asserts the contract's
  vocabularies never drift from their authorities.
- Fixed the PASS 2 `removals` JSON Schema item type under the R1 candidate-3
  closure review: the published schema declared array items as objects while
  the runtime validator accepts only `object_id` strings, so a
  schema-conforming response for a non-empty removals list was guaranteed to be
  contract-rejected. The schema now declares string items matching
  `OBJECT_ID_RE`, and a regression test asserts the published schema and the
  live validator agree on valid, invalid-type, invalid-shape and empty
  removals.

## 1.0.0-beta.110 - 2026-10-17

### Changed

- Normalized PASS run storage onto one canonical run root, `Pass-runs/`, whose
  hierarchy mirrors canonical library ownership: a run is filed at the module
  path its cards land in, as in
  `Pass-runs/software-engineering/languages/python/r_a1b2c3d4/`. The retired
  `workspace/skill-staging/<domain>/<book-run>/` layout and its parallel
  "genre" taxonomy are gone, and `PASS/vfx.py` now shares the same run root at
  `Pass-runs/software-engineering/unreal-engine/vfx/<run-id>/` instead of
  keeping `workspace/vfx-authoring/<task>/` as a second convention.
- Replaced descriptive run directory names with short opaque run ids (`r_` plus
  eight hex characters). No generated path segment carries a source title, book
  title, domain, language, unit title, chapter title or timestamp. `pass.py
  start` takes `--owner <module-path>` in place of `--task <slug>`, and
  `start-over` allocates a replacement id rather than naming one.
- Recorded run description as metadata instead of path text: `controller/run.json`
  gains `run_id`, `owner` and a human-readable `label` at run schema 3. A
  schema-2 run is upgraded in place from its own location, so relocating a run
  is a plain directory move.
- Checkpointed staged artifacts as flat content-addressed blobs under
  `controller/checkpoint/blobs/<sha256>` instead of mirroring the staged tree
  under `controller/checkpoint/files/<path>`. The old nesting reproduced a full
  library-relative card path inside every checkpoint.
- Validated run ownership against the library instead of against a taxonomy cap
  the run layout invented. `OWNER_MAX_PARTS` and `OWNER_MAX_CHARS` are gone;
  `resolve_owner` requires an owner to resolve to an existing module directory
  under `library/<domain>/` or to a new leaf directly beneath one, and the only
  bound on depth is the total path budget. `parse_owner` remains shape-only so an
  existing run stays openable after its library module is renamed or retired.

### Fixed

- Fixed the Windows path-length defect that made real runs fail mid-copy. A live
  run reached 300 absolute characters, past the 260-character limit, because an
  86-character source-title directory sat above a 158-character library card
  path. The same work now peaks at 198 characters, and PASS does not require the
  machine to opt into Windows long paths. `start` refuses a run root over
  `RUN_ROOT_BUDGET`, `check_path_budget` names an over-long path instead of
  letting Windows fail obscurely, and `tests/test_architecture.py::RunPathBudgetTests`
  holds the measured per-domain worst case to account.

### Added

- Added a regression test for `Run.recover()`, which previously had none, now
  covering restoration of controller state and staged files from checkpoint
  blobs after a simulated hard interruption.

### Removed

- Removed `workspace/_diag_paths.py`, a task-owned diagnostic marked
  delete-after-use whose target run no longer exists and which had no referrers.
- Removed the run-schema-1 in-memory upgrade branch. No retained run requires it:
  every live run is schema 2, verified by reading each `controller/run.json`.

## 1.0.0-beta.107 - 2026-10-12

### Added

- Retained three provisional software engineering memory lessons from accepted
  Rust SQLite work: nonvacuous regression setup, rollback evidence at insert and
  commit, and append-only guards covering replacement-on-insert.
- Preserved the supporting ordinary-project observations with explicit limits;
  no canonical card changes or retention/transfer claims.

## 1.0.0-beta.108 - 2026-10-12

### Added

- Retained two provisional software engineering memory lessons from accepted
  Rust context-planning work: scarce-capacity admission must be charged in the
  same priority order as final selection, with typed non-consumption reasons;
  and absence claims at a boundary are proved by doc-stripped production source
  scans paired with behavioral probes.
- Preserved the supporting ordinary-project observations with explicit limits;
  no canonical card changes or retention/transfer claims.

## 1.0.0-beta.106 - 2026-10-12

### Added

- Added six provisional software engineering memory principles from tested Rust
  runtime and backend integration: authority-scoped request identity,
  admission-before-activation rollback, generation-safe reader-visible residency
  commits, fencing versus physical cancellation and retry safety, capability and
  telemetry evidence boundaries, and protocol-phase timeout/error-wrapper tests.
- Preserved the supporting ordinary-project observations in training history,
  with explicit verification limits and no retention or transfer claims.

## 1.0.0-beta.105 - 2026-10-04

### Changed

- Source runs may now live one genre subfolder below their domain
  (`workspace/skill-staging/<domain>/<genre>/<book-run>`) as well as directly
  under the domain. `resume`, domain-based run discovery, and duplicate-source
  detection all follow runs into that subfolder, and closing a run prunes the
  genre folder once it is empty.

## 1.0.0-beta.104 - 2026-10-03

### Changed

- Project snapshots no longer carry `workspace/skill-staging/` authoring state
  for any domain (the selected-domain inclusion, and the older art allowance,
  are removed). Skill-staging exists to keep the library clean while PASS runs
  author new cards, and it never travels in an archive; runs resume from the
  verified checkpoint in the repository's workspace.

## 1.0.0-beta.103 - 2026-10-03

### Added

- Added the 131-card `software-engineering/languages/python` module, covering
  Python syntax, control flow, functions, classes, collections, exceptions,
  decorators, metaclasses, files and I/O, imports and packages, iteration,
  numbers, debugging, performance, and documentation.
- Added an execution-engine note to the "Make the Benchmarked Work Observable"
  pattern, clarifying that the discarded-call trap applies to optimizing and
  JIT engines, not to a plain bytecode interpreter such as CPython.

### Changed

- Added the Python module to the canonical SkillForge Software Engineering
  release recipe, which now lists all six software-engineering modules.
- Moved the Rust-book run scratch files (plan, preflight record, processing
  script) from the repository root into `workspace/scratch/`.

## 1.0.0-beta.102 - 2026-10-03

### Added

- Added the 89-card `software-engineering/languages/rust` module, covering Rust
  project tooling, ownership, types, collections, error handling, traits,
  concurrency, testing, macros, packages, and executable practice.
- Added the language-agnostic CLI stream-routing Pattern to
  `software-engineering/core/error-handling` and included the Rust module in the
  canonical SkillForge Software Engineering release recipe.

## 1.0.0-beta.101 - 2026-09-27

### Added

- Added the 76-card `software-engineering/ai-systems` module for engineering AI
  and agent systems, covering context engineering and cross-session memory,
  deterministic orchestration, multi-agent design, evaluation, inference and
  runtime operations, observability, security, tool use, and task-scoped
  isolation.

## 1.0.0-beta.100 - 2026-09-27

### Fixed

- `test_shipped_memory_is_read_only` skips with an explicit reason when the
  suite runs as root. Root bypasses file permission bits, so `os.access`
  reports every file writable and the test cannot observe a read-only release.
  The check itself, and the read-only behavior of built releases, is unchanged
  and still runs for every non-root user.

## 1.0.0-beta.99 - 2026-09-27

### Fixed

- `memory.py` no longer treats a literal JSON argument as a file path. `entry
  add|update|supersede --json` and `append --json` parse a value whose first
  non-space character is `{` or `[` directly, without probing the filesystem;
  any other value must be a readable JSON file. Before, the argument was
  stat()ed first, which raised ENAMETOOLONG on Linux for JSON longer than a
  filename and could have read an unrelated file whose name matched the text.
  `append` now refuses a non-object `--json` cleanly instead of crashing.
- Added regression tests: long literal JSON through `entry add` and `append`,
  a JSON file path, a missing file, a non-object event, and a unit test that
  literal JSON never touches the filesystem.

## 1.0.0-beta.98 - 2026-09-27

### Fixed

- The Source Prep table-signal test still expected the pre-beta.87 `warning`
  status. Since Source Prep schema 5, numbered-table evidence with zero
  structured tables is an explicit review requirement and the integrity gate
  reports `review`. The renamed
  `test_table_signal_requires_review_when_no_structured_tables_detected` now
  asserts `review`, the table requirement in `review_requirements`, its arrival
  in the preflight acceptance audit's `source_review`, and the warning that the
  preflight packet still shows. Source Prep is unchanged.

## 1.0.0-beta.97 - 2026-09-27

### Fixed

- `test_prepared_pdf_preflight_requires_machine_readable_coordinates` built its
  schema-2 and schema-1 records from the current schema-3 template without
  removing the schema-3-only `language_policy` key, so the parser correctly
  refused them. The test now builds genuine legacy shapes, also covers the
  current schema, and asserts that a schema-2 record carrying `language_policy`
  is still refused. The preflight parser is unchanged.

## 1.0.0-beta.96 - 2026-09-26

### Added

- Added `tests/test_ap_terminology.py`: AP must always expand to Action Protocol.
  The test scans cards, docs, memory, the changelog and tool text for any other
  "action P-word" expansion and for an `AP (...)` expansion that is not
  Action Protocol. Quoted text is exempt so a repair can name the wrong form.

### Fixed

- The beta.84 Unreal editor entry said "Action Procedures"; it now says Action
  Protocols.

## 1.0.0-beta.95 - 2026-09-26

### Added

- CRQ stage 5: `prepare-synthesis` (only while a run is `prepared`, never
  changing state) packs every cited event exactly once, six per leaf batch,
  checks each `summary.json` against the events under its batch, merges four
  summaries per parent until one remains, re-derives every level on each call,
  refuses a parent that drops a child's contradiction, surfaces failures and
  conflicts first, and writes `synthesis/input.json` when complete.
- CRQ stage 5: `evaluate` also writes a `synthesis/disposition.json` template and
  a review brief. `finalize` accepts a disposition that restates the frozen
  status, a section 40 synthesis decision (only a qualified candidate may be
  accepted) and a section 28.2 memory recommendation, writes
  `synthesis/report.md` with the recommended headings, freezes both, and closes
  the run read-only. It writes neither `library/` nor Skillset Memory.
- `PASS/docs/CANDIDATE_REFINEMENT.md`, the CRQ contract, replaces
  `PASS/docs/CANDIDATE_REFINEMENT_DESIGN.md`. A frozen step is never revised in
  place: an unmatched candidate action blocks the freeze until the staged files
  are corrected, a different set of actions is a fresh run, and a synthetic stress
  case found out of scope after the plan froze is replaced in a fresh run rather
  than removed. `environment` holds only comparison-relevant facts; incidental
  details go in `notes` or the `executor` block.
- `ARCHITECTURE.md` contract item 21 defines CRQ as a factory/runtime empirical
  refinement mechanism. `MEMORY_SCHEMA.md`, `SOFTWARE_CARD_FIELD_TESTS.md` and
  `PASS_CONSUMPTION.md` cross-reference it, and `README.md` gains "Refine a
  candidate card from empirical evidence".
- `AGENTS.md` and `CLAUDE.md` share the rule lead "Candidate qualification never
  edits canon automatically."
- Added `tests/test_candidate_qualification_synthesis.py`.

### Changed

- The execution brief says `environment` holds only comparison-relevant facts
  (toolchain and runtime versions, model id, relevant flags) and that timestamps,
  paths and hostnames belong in `notes` or `executor`, which are not compared.
- To stay inside the 8 KiB cold-start budget, `AGENTS.md` and `CLAUDE.md` drop
  two sentences that restated what already precedes them ("Edit a lead here,
  edit it there." and "Do not treat it as a constraint to preserve.").

### Removed

- `PASS/docs/CANDIDATE_REFINEMENT_DESIGN.md`, superseded by
  `PASS/docs/CANDIDATE_REFINEMENT.md`.

## 1.0.0-beta.94 - 2026-09-26

### Added

- CRQ stage 4: `open-execution` writes a result template for both arms of every
  case (bound to the frozen case definition's SHA-256), builds and freezes
  `arms/baseline/cards/` and `arms/candidate/cards/` (the baseline with the
  frozen candidate laid over it), and replaces the brief with the execution brief,
  which now reveals held-out cases.
- CRQ stage 4: `freeze-execution` validates every arm result: a closed key set;
  verdict pass, fail or invalid with no partial result; a pass only when every
  frozen success criterion passes and a fail only when one fails; invalid only
  with a reason; the planned evaluation mode and evaluator relation; a named
  executor; hashed evidence under `evidence/`, every file listed; suspected
  contamination refused until resolved and confirmed contamination only on an
  invalid arm. It then freezes all results and evidence.
- CRQ stage 4: `evaluate` checks arm symmetry (both results graded against the
  frozen case definition and declaring the same environment; a mismatch makes that
  comparison invalid), computes each case's delta, applies the section 23 gate, and
  writes and freezes `qualification_result.json` with the deltas, blocking and
  positive cases, synthetic cases, the protection gap, change accounting
  (accepted-for-synthesis-review, rejected-by-qualification or
  applied-to-candidate) and `canon_modified: false`.
- `PASS/runtime/candidate_qualification/gate.py` holds the pure per-case delta
  and final gate: invalidity (any required invalid comparison or any confirmed
  contamination), protected regression, target failure, synthetic stress,
  protection gap, positive improvement, qualified. Non-required cases never
  decide the status and synthetic success never counts.
- Added `tests/test_candidate_qualification_gate.py` (every delta pair, every
  rule, every adjacent precedence pair, the aggregate net-win case) and
  `tests/test_candidate_qualification_execution.py` (design fixtures A and B end
  to end, result validation, symmetry, contamination, the frozen result).

### Changed

- `status` counts an arm result with no verdict yet as missing.

## 1.0.0-beta.93 - 2026-09-26

### Changed

- The CRQ controller is split into the `PASS/runtime/candidate_qualification/`
  package: `schemas.py` (vocabularies, errors, hashes, atomic JSON, path
  containment and document validation), `evidence.py` (memory intake, canon
  reading, candidate accounting, overlay validation), `controller.py` (run
  state, freezes, drift and the lifecycle commands) and `gate.py` (reserved for
  the execution-stage gate). `PASS/runtime/pass_candidate_qualification.py`
  remains the command line and only parses arguments. The move changes no
  behavior.
- The CRQ controller fingerprint now covers every package file plus the entry
  script: each file LF-normalized and hashed, the (relative path, hash) pairs
  sorted by path and combined into one SHA-256. Runs prepared before this
  version no longer match and can only be closed or discarded.

## 1.0.0-beta.92 - 2026-09-26

### Fixed

- The CRQ controller reads every card (frontmatter, sections, the evidence
  scan) through one decoder that treats CRLF and LF alike; the line endings are
  normalized only for parsing and the whitespace-only comparison, and every card
  and evidence hash stays byte-exact.
- The CRQ tests write fixtures as exact bytes, so Windows no longer turns the
  synthetic library into CRLF and the line-ending cases behave the same on every
  platform. New tests stage and freeze a CRLF baseline and candidate, refuse a
  CRLF-to-LF conversion as whitespace-only, and check that both endings parse
  alike while hashing differently.

## 1.0.0-beta.91 - 2026-09-26

### Added

- CRQ stage 3: `freeze-plan` validates `controller/qualification_plan.json` and
  every `cases/<id>/case.json` against closed vocabularies (role, origin,
  evaluation mode, visibility, evaluator relation), then freezes the plan, each
  case and each listed fixture. Synthetic cases are protected stress probes only:
  never positively eligible, never citing an event, and each states why it stays
  inside the card's contract. Empirical cases cite valid, uncorrected,
  unquarantined history events; a required semantic case needs a separate
  evaluator; a deterministic case is checked deterministically. The plan needs a
  required non-synthetic eligible target and records `protected_case_gap` exactly
  when no required non-synthetic protected case exists. Unplanned case folders,
  premature result folders and unlisted or changed fixtures are refused.
- CRQ stage 3: `stage-candidate` refuses any assessment that is not a
  canon-candidate, copies each revised card byte-for-byte from the frozen baseline
  into `candidate/cards/`, creates only the empty folder for a new card, writes a
  candidate manifest template, and rewrites the brief for the candidate author
  with author-visible target cases only; held-out cases are counted, never shown.
- CRQ stage 3: `freeze-candidate` accounts for every authorized action and every
  staged file (missing, byte-identical, whitespace-only, renamed, retyped,
  unauthorized, moved or support-card copies are unmatched and block the freeze),
  refuses cards that name the run, its memory entry, events, cases or workspace,
  enforces the scope ceilings, then lays the candidate over a temporary copy of
  the live library and runs `validate.py` and `verify_references.py` with
  `--library` through their own `main()`. The overlay is removed on success and
  failure. The frozen manifest records baseline and candidate hashes, computed
  changed sections, the author's rationale and the scope counts.
- `freeze-assessment` writes a qualification-plan template; the operator brief
  documents the plan and case format.
- Added `tests/test_candidate_qualification_candidate.py`.

## 1.0.0-beta.90 - 2026-09-26

### Added

- CRQ stage 2: `prepare` starts a run from one Skillset Memory `card_candidate`.
  It resolves the entry through `PASS/tools/memory.py` (the whole store must
  validate; the entry must be an active or monitoring candidate citing only valid,
  uncorrected, unquarantined events), resolves object-id likely owners inside the
  run's domain plus `metaskills` without reading any other domain, freezes the
  entry and its cited events as `controller/intake.json`, snapshots a bounded
  baseline (targets, their transitive hard prerequisites, one hop of their other
  links, and owning `MODULE.yaml` files), and writes an assessment template and an
  operator brief. Run ids are allocated from the memory entry prefix by scanning
  only that domain's run folder.
- CRQ stage 2: `freeze-assessment` validates and freezes
  `controller/assessment.json`: closed dispositions and attributions, the Skillset
  Memory failure-layer vocabulary, canon candidates limited to knowledge,
  orchestration or training failures attributed to `skillcard`, owners and
  revisions confined to the frozen baseline and the active domain, an exposure
  check when the cited evidence records exposed cards, routing reasons for
  layer/object-type mismatches, `revise`/`create` actions only, and the run's
  scope ceilings. Non-canon dispositions freeze for the record with no actions.
- Added `tests/test_candidate_qualification_intake.py`.

### Changed

- CRQ `invalidate` and `abandon` no longer require the preparing controller's
  fingerprint; `run.json` records the closing controller's fingerprint in
  `closing_controller_sha256` beside the original.
- The CRQ controller fingerprint hashes its source with CRLF normalized to LF;
  card and evidence hashes remain byte-exact.

## 1.0.0-beta.89 - 2026-09-26

### Added

- Added `PASS/runtime/pass_candidate_qualification.py`, stage 1 of the Candidate
  Refinement & Qualification (CRQ) controller: the schema-1 `controller/run.json`
  record, the linear run state machine with `invalidated` and `abandoned` exits,
  atomic state writes with read-back, bounded run-relative paths that refuse
  symlink escape, SHA-256 freeze records, the controller fingerprint check, and
  baseline-drift verification against both canon and the run's frozen snapshot.
  Its commands are `status`, `invalidate` and `abandon`; the lifecycle commands
  arrive in later stages. The controller never writes `library/` or Skillset
  Memory and calls no model.
- Added `tests/test_candidate_qualification_state.py` for state transitions,
  wrong-state refusal, resume and read-back, interrupted writes, the controller
  fingerprint, path containment and baseline drift.

### Changed

- `PASS/docs/PASS_RUN.md` §Workspace lifecycle registers the
  `workspace/candidate-qualification/` bucket with its owner, layout and cleanup
  condition.

## 1.0.0-beta.88 - 2026-09-26

### Added

- Added `PASS/docs/CANDIDATE_REFINEMENT_DESIGN.md`, the proposed design for Candidate
  Refinement & Qualification (CRQ). It is a working input for the CRQ implementation branch and is
  replaced by `PASS/docs/CANDIDATE_REFINEMENT.md` before that branch merges. No runtime behaviour changes.

## 1.0.0-beta.87 - 2026-09-25

### Added

- Added Source Prep schema 5 integrity severity: `fail`, `review`, `warning`,
  and `pass`. Strong PDF/font decode corruption on code-bearing pages now fails
  closed instead of reaching preflight as apparently valid text.
- Added retained whole-page integrity fallback images for suspicious decode and
  unstructured numbered-table evidence. The fallback is review evidence only;
  Source Prep never silently OCRs or reconstructs missing source content.
- Added deterministic prepared-PDF unit-boundary auditing. Overlapping units and
  strong heading/material matches assigned to a neighboring unit block preflight;
  implausibly tiny spans and weaker heading mismatches are surfaced for review.
- Added `workspace/tools/test_pass_source_quality.py` regression coverage for
  corruption detection, legacy table warnings, unattended acceptance blocking,
  and Karumanchi-style boundary drift.

### Changed

- Numbered-table evidence with zero structured preservation is now an explicit
  review requirement. Unattended authorization cannot auto-accept a preflight
  while Source Prep or boundary review requirements remain; explicit
  human/frontier confirmation may still accept after inspection.
- Legacy prepared-source schema 3/4 table/code sanity warnings are upgraded into
  the new review gate at acceptance time instead of being silently grandfathered.
- PDF C1 control characters commonly produced by broken bullet/list glyphs are
  recorded but no longer treated as code corruption by themselves, avoiding
  false failures on otherwise healthy technical books.
- Source Prep, PASS run, runtime, README, and skill documentation now describe
  the fail-closed corruption gate, visual fallback policy, table review rule,
  and unit-boundary coherence checks.

## 1.0.0-beta.86 - 2026-09-25

### Added

- Added `PASS/pass.py start-over`, a first-class reset transition for explicit
  user instructions to start over/reset/discard an unfinished source run. The
  command does not ask the model to reconcile old checkpoints before obeying the
  reset; it makes the old continuation chain ineligible and creates a fresh run
  identity.
- Added three explicit reset boundaries: `--from scratch`, `--from source_prep`,
  and `--from preflight`, plus optional `--carry-notes`. Only the named artifacts
  may seed the replacement run. Source-Prep reuse requires a verified package;
  preflight reuse additionally requires an accepted eligible plan.
- Added a durable `controller/reset-intent.json` transaction marker. If reset is
  interrupted, the old run is blocked from resume/recover/save until the same
  start-over transaction finishes, preventing a stale process or checkpoint from
  resurrecting abandoned controller state.
- Added start-over regression coverage for stale operation locks, notes-only
  scratch reset, verified Source Prep reuse, accepted preflight reuse, old-state
  resurrection blocking, and legacy Software Engineering preflight rejection.

### Changed

- `start-over` archives and clears stale operation leases from dead processes,
  revokes unattended/action leases, and refuses to race a PID that still appears
  live.
- Reusing `source_prep` deliberately removes unit files materialized from the
  abandoned plan before rerunning preflight. Reusing `preflight` rematerializes
  units from the carried accepted plan and begins at U01 PASS 1 with no carried
  PASS 1/2/3 state.
- Software Engineering schema-1/2 preflights cannot be reused as the starting
  point of a new reset run because they predate beta.85's mandatory language
  policy. Such runs must restart from verified Source Prep so preflight can
  establish the current-version modernization contract.

## 1.0.0-beta.85 - 2026-09-25

### Added

- Added preflight schema 3 for Software Engineering language work. New
  Software Engineering preflights must explicitly classify the source as
  `programming-language` or `not-programming-language`. Programming-language
  sources declare the language, current target version, target-version basis,
  and mandatory modernization policy before PASS 1 begins.
- Added PASS 1 `version_sensitive_flags` and a PASS 2
  `language_modernization` audit. Every flagged source-era claim must resolve as
  current, modernized, historical, or rejected against the accepted target
  version, with explicit current guidance and verification evidence.
- Added PASS 3 semantic checks for `core_language_agnosticism` and
  `language_modernization` on programming-language runs.
- Added regression coverage for schema-3 round trips, schema-2 recovery,
  mandatory modernization, phase templates, modernization resolution, and
  schema-downgrade rejection.

### Changed

- Software Engineering Core ownership is now mechanically constrained against
  specialized routing: `software-engineering/core/` cards must keep
  `specialization_axis: none` and may not use `routing_class: specialized`.
  PASS 2 additionally requires an explicit agnosticism review for every Core
  card changed by a programming-language run.
- Stateful preflight persistence now uses the canonical preflight serializer
  instead of generic dataclass serialization, preserving schema-specific
  language policy through initial submission, revision, and unit replanning.
- Software Engineering language authoring doctrine now distinguishes immutable
  source-era evidence from current instructional guidance: source text is
  preserved, while version-sensitive library instruction is always reconciled
  to the accepted current target version.
- `PASS_LIBRARY.md` is now part of the required authoring document set so the
  Core/language ownership contract is loaded before a new run proceeds.

### Compatibility

- Existing schema-1 and schema-2 preflight plans remain readable and resumable.
  A schema-3 Software Engineering plan cannot be revised or replanned into a
  legacy shape that silently drops its language policy.

## 1.0.0-beta.84 - 2026-09-24

### Added

- Completed the 20-unit software-engineering study of Roger Mattsson's
  *Extending and Customizing Unreal Engine Editor*. The canonical library now
  contains 67 cards from the source: 40 Patterns, 15 Action Protocols and 12
  Drills.
- Added reusable Unreal guidance for editor previews, Slate browsers, asset and
  Blueprint validation, World Partition migrations, component visualizers,
  secure Data Table synchronization, latent actions, reflection-safe wildcard
  thunks, custom K2 compiler expansion and lifecycle-safe subscription nodes.
- Added an end-to-end K2 subscription-node drill during source closure to join
  reconstruction, compiler lowering, runtime cleanup and cooked-module
  verification.

### Changed

- Refined the existing Unreal editor module-boundary, command-routing and
  shared-versus-local settings cards against the completed source.
- Regenerated software-engineering and Unreal navigation indexes for the new
  editor and Blueprint material.

### Evidence

- Completed deterministic Source Prep for all 287 PDF pages, including 46
  visually significant segments and 1,231 preserved code blocks; verified and
  finalized the prepared package before continuing at U06.
- PASS reported all 20 units accepted, source closure complete, schema
  validation passing and reference verification passing.

## 1.0.0-beta.83 - 2026-09-24

### Fixed

- Repaired the unit materializer's page-coordinate resolution. A locator such as
  `pp. 3-26 (PDF 55-78)` now resolves from the explicitly labelled PDF/source
  range instead of the first numeric range, so prepared units start and end on
  the authoritative PDF pages. One unlabelled range remains supported for legacy
  plans; multiple ambiguous unlabelled ranges and conflicting explicit ranges
  fail closed instead of guessing.
- Made unit materialization fail closed. Before a unit file is accepted, the
  materializer verifies that every required prepared page exists, that each page
  declares the expected `source-page` marker, and that the generated unit carries
  the exact contiguous marker sequence for the authoritative range.
- Added an independent numbered-table sanity signal to Source Prep. A source
  with at least three numbered table captions but zero structurally detected
  tables now records an integrity warning, carried into the preflight
  presentation packet under `SOURCE PREP INTEGRITY WARNINGS`, instead of
  silently implying that tables were converted successfully.

### Added

- Preflight schema 2 as the preferred schema for new runs: each unit carries
  machine-authoritative `source_pages` separately from human display metadata
  (`locator`, `printed_pages`). Prepared-PDF preflight records are blocked before
  presentation when `source_pages` is missing or outside the prepared PDF.
  Schema-1 plans remain readable so legacy runs can be repaired without
  repeating preflight.
- `status` and `resume` now expose the Source Prep integrity status and package
  hash alongside the controller state.

### Evidence

- Regression-tested the repaired legacy parser: `pp. 3-26 (PDF 55-78)` resolves
  to 55-78; one unlabelled range stays supported; multiple ambiguous unlabelled
  ranges and conflicting explicit ranges fail closed.
- Regression-tested schema-2 coordinate gating: valid `source_pages` passes;
  missing or out-of-range `source_pages` on a prepared PDF is blocked before
  presentation; schema-1 explicit-PDF plans remain supported.
- Rematerialized the active Learning Python run against the repaired
  materializer: all 41 units match their explicit PDF ranges exactly with zero
  marker/range errors; `prepared-source/source.json` and the controller package
  hash were refreshed and a verified recovery checkpoint was created. The
  1,594-page Source Prep was not rerun.
- Synthetic source with three numbered table captions and zero structured
  tables produces the integrity warning, and the warning appears in the
  preflight presentation packet.
- Full test suite green: 337 tests on Python 3.14 for Windows.

## 1.0.0-beta.82 - 2026-09-23

### Fixed

- Canonicalized temporary overlay roots before indexing and comparing staged
  card paths. This prevents Windows 8.3 short-path spellings from conflicting
  with their resolved long-path equivalents during PASS 2 and PASS 3.

### Evidence

- Re-ran the refinement-overlay and legacy Source Prep backfill regressions on
  Python 3.14 for Windows, where the temporary-directory API returned the short
  user-profile spelling and copied card paths resolved to the long spelling.

## 1.0.0-beta.81 - 2026-09-23

### Added

- Added an explicit legacy Source Prep backfill path for planned, post-preflight
  runs that began before Source Prep existed. The compatibility path binds the
  original source identity, prepares and verifies the complete source package,
  materializes the accepted unit plan, and resumes the exact active phase.

### Fixed

- Preserved accepted preflight state, unit index, staged cards and cumulative
  accepted deltas while bringing an active legacy run under the current Source
  Prep and hard-checkpoint contract.

### Evidence

- Added a regression that lands one unit, removes the simulated pre-Source-Prep
  artifacts, performs the legacy backfill, and verifies that every accepted
  progress field and staged-delta hash remains unchanged.

## 1.0.0-beta.80 - 2026-09-23

### Fixed

- Made PDF Source Prep code detection typography-independent. Same-font Python,
  REPL/shell prompts, indented suites, calls, assignments, docstrings, and compact
  console output are now recognized from syntax plus layout instead of requiring
  a monospace face.
- Preserved prompt/output and cross-block indentation without letting nearby
  instructional prose leak into code fences; tightened C/C++ declaration and
  shebang heuristics to avoid lexical false positives.
- Added an independent raw-code/preformatted sanity signal to the Source Prep
  integrity gate so a programming source can no longer report a clean result
  merely because the primary detector found zero code. Structured code tables
  satisfy that sanity check without being misreported as missing code blocks.
- Bumped the prepared-source schema so beta.79 prepared packages are regenerated
  under the corrected detector rather than silently reused.

### Evidence

- A 115-page real Python programming source now prepares with 250+ preserved
  code/REPL regions, including indentation-sensitive `if`/`for`/`while` examples
  that use the same serif font as body prose, with the integrity gate passing.
- Re-ran the 112-page Unreal/C++ Chapters 1-4 regression fixture: printed
  `real-world` punctuation remains intact, all detected code is preserved, 11
  structured tables and 83 significant visuals remain routed, and the integrity
  gate passes without false code-missing warnings from code-bearing tables.

## 1.0.0-beta.79 - 2026-09-23

### Changed

- Refined PDF Source Prep into a semantic model-facing layer over the retained
  deterministic extraction floor. Prepared pages now preserve code/preformatted
  indentation, expose headings and lists as Markdown, fence detected code/REPL
  regions, structure suitable tables, and inventory significant visuals as
  on-demand assets instead of discarding them.
- Prepared-source indexes and unit files now make PDF/source page coordinates
  explicit and surface detected tool/version compatibility signals before PASS
  canonicalization.
- Large HANDOFF checkpoints summarize recoverable file groups while the
  checkpoint manifest remains the exhaustive per-file hash authority.

### Fixed

- Removed destructive global whitespace collapsing from Source Prep so
  indentation-sensitive languages such as Python retain executable structure.
- Made printed-hyphen line joining conservative: ambiguous hyphens are retained
  rather than silently deleting real source punctuation (for example,
  `real-\nworld` remains `real-world`).
- Added code-preservation and lexical-coverage integrity measurements to prepared
  segments; Source Prep fails verification if a detected code block is not
  preserved in the model-facing package.

## 1.0.0-beta.78 - 2026-09-23

### Added

- Added verified hard checkpoints for ordinary PASS runs. Each checkpoint now
  carries the complete controller state plus recoverable staged/prepared files;
  `PASS/pass.py recover` restores the last verified transaction after a hard
  interruption instead of requiring the next model to infer where work stopped.
- Added deterministic Source Prep before ordinary preflight. Prepared sources
  preserve model-facing content under the active skill-staging run, bind every
  prepared file to the source identity, and can be verified/reused without
  repeating extraction. Runs may stop cleanly after Source Prep or after
  accepted preflight and later continue from that exact state.
- Added crash-safe final canonicalization journaling so an interruption during
  source close can restore the pre-close canonical bytes before resuming.

### Changed

- Ordinary unit landing now accepts the reviewed delta into cumulative
  `workspace/skill-staging/` state. Later units reconcile against canonical
  knowledge plus the accepted source delta; only successful source closure
  canonicalizes the complete staged delta into `library/`.
- Active skill-staging state for a selected domain now travels in continuation
  project snapshots, making the archive plus HANDOFF/checkpoint sufficient for
  model/provider switching. SkillForge releases remain free of authoring state.
- Renamed ordinary authoring scratch to `workspace/skill-staging/` and project
  snapshot output guidance to `workspace/project-releases/`. Workspace-local
  disposable temporary files belong under `workspace/tmp/`.
- Domain-scoped project snapshots now include only the canonical SkillForge
  release recipe(s) for the selected domain(s), rather than every domain recipe.

### Fixed

- HANDOFF now advances only with a verified checkpoint and reports the exact
  recover/continue state, Source Prep state, stop target, and staged-delta state.
- A stale operation/landing lease left by a dead PASS process can be retired by
  verified recovery without silently accepting partial work.

## 1.0.0-beta.77 - 2026-09-22

### Added

- Added a skeleton Unreal/Niagara VFX PASS lane (`PASS/vfx.py`) for durable
  runs against existing effects: inventory, whole-system/isolated capture
  coverage, visual/implementation classification, staged Recipe/Drill/AP
  extraction, and visual validation.
- Added `workspace/tools/extract_vfx_stills.py`, a temporal VFX adapter over the
  existing video-stills engine. It samples whole-system and solo emitter/component
  recordings uniformly and keeps every planned time sample for temporal review.
- Added a self-contained Niagara recipe library under
  `software-engineering/unreal-engine/vfx/niagara/recipes/`, organized by effect
  family with family-local variant and visual-style tags. Patterns are Recipes;
  APs are Composite Recipes.

### Changed

- VFX Recipes no longer carry book/page/source identity or runtime links to
  other recipes. Composite Recipes contain the full procedure they need, while
  generated family indexes provide navigation.

## 1.0.0-beta.76 - 2026-09-21

### Added

- Added 70 Unreal Engine VFX cards covering Niagara effects, modules, events,
  Blueprint controls, debugging, performance, and reusable practice drills.
  The cards are part of the existing `software-engineering/unreal-engine` module.

## 1.0.0-beta.75 - 2026-09-20

### Fixed

- Replaced the Unreal Blueprint cards with the audited set. Fourteen cards
  changed: overclaimed rationale is cut back to what the source actually
  demonstrates, `foundation_role` / `routing_class` / `specialization_axis` are
  corrected where a specialization had been recorded as a foundation and the
  reverse, missing `foundation_object_id` and prerequisite edges are supplied,
  and the save-and-load Action Protocol now delegates its validity guard, type
  cast and coarse-state decisions to the Patterns that own them instead of
  restating them, with an end-to-end verification step.

### Removed

- `PAT_use_a_validated_get_to_branch_on_a_reference_validity` is absorbed into
  `PAT_guard_object_references_with_is_valid` as the variant
  `VAR_use_a_validated_get_at_the_reference_read`. Both describe the same
  validity decision; one expresses it at the variable read. Nothing else
  referenced the removed card.

## 1.0.0-beta.74 - 2026-09-20

### Changed

- A batch run in `workspace/tools/extract_video_stills.py` now writes into a
  folder named after the source, inside the output folder you pick, holding a
  copy of the source's subfolder structure. Choosing `D:/Exports` for a course
  called `C++ Multiplayer Shooter` puts the bundles and `batch_report.json`
  under `D:/Exports/C++ Multiplayer Shooter/`, so one export folder can take
  course after course without their sections landing among each other. An
  output folder inside the source is left as it is, because the name would only
  repeat the folder above it, and leaving the output folder empty still writes
  to `_stills` inside the source.

## 1.0.0-beta.73 - 2026-09-20

### Added

- Ordinary source runs now enter a mandatory source-closure audit after the
  final unit lands instead of jumping directly to `finished`. Closure explicitly
  audits AP synthesis, DRILL synthesis, cross-library reconciliation, and
  metadata classification; any justified closure delta receives its own
  card-only PASS 3 and landing gate.
- PASS 2 now records nearest-owner reconciliation and explicit
  `stage_binding` / `lane_fit` / `confidence` classification for every changed
  card. PASS 3 includes matching semantic checks.

### Fixed

- Repaired six Blueprint cards found by the completed book audit: container
  validation is now precondition-specific; array invalidation no longer blames
  growth; enum use no longer requires Switch; Sequence no longer implies latent
  completion; frame-rate scope is an investigation signal rather than proof of
  cause; and Blueprint float tolerance is linked to the general floating-point
  foundation.
- Unattended source orchestration now dispatches, audits, presents, and lands the
  source-closure phases instead of treating the last unit as source completion.

## 1.0.0-beta.72 - 2026-09-20

### Changed

- `workspace/tools/extract_video_stills.py` looks for speech models beside the
  program first, then in per-user application data. The packaged tool is now a
  self-contained folder holding the executable and a `models/` directory, so it
  can be moved or copied whole and the model travels with it. Per-user
  directories are still searched, including the one next to the settings file.
- The "no speech model" messages name the folder beside the program rather than
  a per-user path, and say that the ? beside ffmpeg lists every location tried.

### Added

- The ? beside ffmpeg in the window reports live diagnostics: whether the
  program is frozen, where it runs from, the settings file, every directory
  searched for models, what was found in each, and what it resolved. `--doctor`
  prints the same report, which the two now share. The packaged program has no
  console, so without this an operator has no way to see what it resolved.

## 1.0.0-beta.71 - 2026-09-20

### Added

- `--doctor` in `workspace/tools/extract_video_stills.py` reports whether
  ffmpeg, ffprobe, a whisper speech model and a voice-detection model can be
  found, and lists every directory searched. Added after a packaged build
  reported no speech model while the file sat in the directory its own error
  message named; the script was correct and only the executable was stale.

### Changed

- The module header records that the PyInstaller work directory must be
  deleted between builds. Reusing it produced an executable that did not match
  the source.

## 1.0.0-beta.70 - 2026-09-19

### Added

- `workspace/tools/extract_video_stills.py` gains content presets, a
  tile-based comparison mode, batch folder conversion and optional speech
  recognition. Presets (general, vfx, blueprints, code, slides, software) fill
  the existing controls and are then out of the way, so a manual change after
  choosing one is what runs. The new `sensitive` comparison compares a 16x9 grid
  of screen tiles instead of the whole frame, keeping a still when one corner of
  a node graph or property panel changes; the original whole-frame hash remains
  the default. Batch mode converts a folder, mirroring its structure, skipping
  videos without subtitles and bundles already built, surviving unreadable files
  and recording every item in `batch_report.json`. Transcription uses ffmpeg's
  own whisper filter when a video has no subtitles, and marks the result as
  machine-generated in both the transcript and the manifest.
- `workspace/tools/test_extract_video_stills.py`, 79 tests covering the above.
  Tests needing ffmpeg build a synthetic screencast with known changes and skip
  themselves when ffmpeg is absent, so the PASS suite gains no new dependency.

### Fixed

- The stills tool no longer leaves ffmpeg running after its window closes.
  Child processes outlive the Python interpreter that started them, so closing
  during a transcription orphaned a process holding a multi-gigabyte speech
  model. Cancel now stops a transcription too, rather than waiting for it.
- Single-file mode can transcribe without a subtitle file, which it previously
  refused, and worker threads no longer read Tk variables off the main thread.

## 1.0.0-beta.69 - 2026-09-19

### Added

- Fifteen Unreal Engine Blueprint Patterns in
  `software-engineering/unreal-engine/blueprints/`, landed by units u05, u06 and
  u07 of the Blueprints visual-scripting run: materials (authoring one by wiring
  parameter nodes, metallic and roughness, a swappable material asset, swapping
  at runtime), actors and motion (subclassing a level actor in place, keeping
  actors static unless manipulated, per-frame movement scaled by delta time,
  looping timers), and player abilities (action versus axis mappings, restoring
  the base value on release, timelines instead of snapping, projectile speed
  profiles, effects at the hit location, two-stage interaction as a boolean and
  branch, investigating an external asset first). The domain indexes are
  regenerated.

## 1.0.0-beta.68 - 2026-09-19

### Added

- Hard checkpoints: every controller operation that changes `run.json` ends by
  copying the run's `drafts/` and `recipes/` into `controller/checkpoint/`, bound
  to that state. Operations that accept nothing never move it.
- `pass.py rollback` restores the drafts to the last checkpoint so an
  interrupted phase restarts from its beginning; stopping inside PASS 3 returns
  to the end of PASS 2. `resume` lists drafts changed since the checkpoint and
  names the rollback as the next action.
- The controller writes the run's `HANDOFF.md` after every checkpoint: last safe
  endpoint, current unit and scope, drafts at the checkpoint, pick-up commands.
  A hand-written handoff is moved into `NOTES.md`, which models own.

### Changed

- PASS 2 stores one fingerprint of the live files it depends on instead of the
  full hash map, which had made `run.json` about 160 KB; older runs still verify.
- `close-run` removes the checkpoint and generated handoff and keeps `NOTES.md`.
- `AUTHORING_RUNTIME.md`, `PASS_RUN.md` and `PASS/SKILL.md` describe checkpoints,
  rollback, the generated handoff, and not reading `run.json` to orient.

## 1.0.0-beta.67 - 2026-09-19

### Added

- Three Unreal Engine Blueprint Patterns in
  `software-engineering/unreal-engine/blueprints/`: calling functions on another
  Blueprint through a direct object reference, testing a type or reaching
  subclass members with Cast, and notifying listeners through an event
  dispatcher without naming them. The domain indexes are regenerated.

## 1.0.0-beta.66 - 2026-09-19

### Added

- `memory.py entry add|update|supersede|show`, the supported way to change a
  `skill_memory.yaml` entry. Each write validates the whole resulting store
  first and refuses with nothing changed; `add` assigns the next id, `update`
  merges fields (null removes an optional key) and never changes an id, and
  `supersede` can add the replacement in the same write. There is no delete.

### Changed

- Store writes are atomic, serialized per domain by a lock in `memory/.locks/`
  (ignored by git and never copied into a release), and splice only the
  changed entries, so untouched entries keep their exact text and the file
  keeps its line endings. `append` and `compact` take the same lock, and
  `compact` now records `last_verified` as a date.
- `MEMORY_SCHEMA.md`, `memory/README.md` and the pass-authoring wrappers make
  `entry` the write path; hand-editing is recovery only.

## 1.0.0-beta.65 - 2026-09-19

### Added

- `library/metaskills/runtime/ap_runner.py`, a metaskills module runtime that
  steps an AP card one step at a time. It shows only the current step plus the
  full text of the Patterns that step names, and unlocks the next step only
  after `done` (what was done), `gate` (an evidenced pass or fail; a fail keeps
  the step current) or `skip` (a reason; never for a gate). `back` reopens an
  earlier step, a changed card stops the run, runs persist in the project's git
  directory, and `record` exports the completion record. It ships once in every
  release with `metaskills`, and its tests check that every installed AP parses.

### Changed

- The software-engineering, generic (writing, agent-kit) and art profiles, and
  the matching repo skill wrappers, require APs to be executed through the
  runner. Art adds that a runner gate never replaces a Staged Production user
  approval gate; the Art Stages themselves are unchanged.
- `EXECUTION_CONTRACT.md` documents what the runner enforces and what it cannot.

## 1.0.0-beta.64 - 2026-09-19

### Added

- Seven more Unreal Engine Blueprint Patterns in
  `software-engineering/unreal-engine/blueprints/`: choosing a gameplay-framework
  base class by role, game rules and defaults in the Game Mode, player input in
  the Player Controller, cross-level state in the Game Instance, storing a
  spawned actor's reference, guarding references with Is Valid, and per-instance
  configuration in the Construction Script. The domain indexes are regenerated.

## 1.0.0-beta.63 - 2026-09-19

### Added

- `pass.py resume` is the re-entry point after any context loss. It is read-only:
  it finds the domain's unfinished run (filtered by `--source`), verifies source
  identity, the operation lock, staged-draft and live-card hashes, reports units
  completed, current unit and phase and the last accepted step, and names one
  next legal action. In unattended mode it defers to `source.py drive`, whose
  lease survives a restart unchanged.
- `pass.py abandon --run --reason` retires an unfinished run on explicit user
  instruction, keeping its drafts and final state for inspection.

### Changed

- `start` refuses a second unfinished run of the same source in the same domain,
  matched by path or, for a moved or renamed copy, by size and SHA-256. It no
  longer forks a book because a fresh context did not know the run existed.
- The operation lock records its process ID and time.
- `PASS/SKILL.md`, the repo skill wrappers and the README tell a model to run
  `resume` before `start`.

## 1.0.0-beta.62 - 2026-09-19

### Added

- Seven Unreal Engine Blueprint Patterns in
  `software-engineering/unreal-engine/blueprints/`: when a Blueprint should be a
  level Blueprint or a class, composing behavior from components, choosing a
  variable type, who may read and write state, separating state from event-driven
  behavior, pure functions, and choosing between a macro, a function or a custom
  event. The domain indexes are regenerated.

## 1.0.0-beta.61 - 2026-09-19

### Fixed

- The `AGENTS.md` / `CLAUDE.md` cold-start budget and the repo skill-wrapper
  budget measured the checkout's bytes, so a Windows clone with
  `core.autocrlf` failed them (one extra byte per line) while the committed text
  was within budget. Both checks now measure with line endings normalized.

## 1.0.0-beta.60 - 2026-09-19

### Changed

- SkillForge releases now live one folder per skill,
  `releases/skills/<domain>/SkillForge-<Name>.zip`, each with a README. The
  README recipe table, its build example and `MODULE_RELEASES.md` point there,
  and the table gains `SkillForge_Agent_Kit.yaml`.

## 1.0.0-beta.59 - 2026-09-19

### Fixed

- Agent Kit runtime 1.1.1: in a shared checkout, `done` now warns when other
  open tasks' uncommitted files were present, since a test run there measures
  their work too, and records those files beside the evidence as
  `uncommitted_other_tasks`. The README shows how to gather evidence on a clean
  worktree at the submitted commit.

## 1.0.0-beta.58 - 2026-09-19

Agent Kit runtime 1.1.0, from the first trial's feedback reports.

### Fixed

- `done` recorded no changed files when work was committed on the base branch,
  so its scope audit saw nothing. A claim now records its starting commit; a
  task's changes are its commits since then whose subject line names it, any
  commit given as evidence, and uncommitted files in its scope. Claims made
  before this fall back to commits since their first claim.
- In a shared checkout, `check` and `done` blamed one agent for another's
  uncommitted work. Uncommitted files inside another open task's scope are now
  labelled with that task; only changes no open task claims are flagged.
- Every command accepts `--as`; `check` rejected it.
- Two globs in one directory always collided. Segments are now compared, so
  `authoring*.py` and `basic*.py` can be held in parallel; undecidable pairs
  still count as overlapping.

### Added

- `--reviewer` on tasks and a `review` verdict command. `accept` requires the
  named reviewer's verdict on the current attempt or a recorded
  `--override-review`, and refuses work the accepting lead did.
- `note`: any registered agent can attach a note to any open task.
- `hold` / `unhold`: short, expiring holds on shared resources such as a running
  editor or a build, shown on the board and respected by claims.
- The board shows priority and lists ready work in the order `next` offers it;
  help and README say higher priority runs first.

### Changed

- Store schema 2, migrated in place on first use; an older runtime refuses the
  upgraded store. README: commit-subject convention, shared-checkout guidance,
  testing a scope against the design before editing.

## 1.0.0-beta.57 - 2026-09-18

### Added

- New-domain lifecycle. `build_project_snapshot.py --new-domain <domain>` builds a
  project for a domain the repository does not have: PASS, `metaskills`, a
  minimal module, placeholder discovery wrappers and recipe, and a handoff.
  `import_project_snapshot.py --create-domain <domain>` imports it with its
  wrappers and recipe. The archive cannot authorize itself; any other unknown
  domain is still refused, and placeholder descriptions block the import.
- Module runtimes. A module may declare executable helpers under its own
  `runtime/` directory in `MODULE.yaml`. `validate.py` enforces the contract:
  declared entrypoints and tests, standard library only, no card-like Markdown,
  and no executable file anywhere else in `library/`. `build` runs each shipped
  runtime's tests on the staged copy, records `module_runtimes` in the manifest
  and names each entrypoint and README in the generated `SKILL.md`.
- The `agent-kit` domain, created through the new lifecycle. Its
  `agent-kit/coordination` module ships a standard-library runtime that keeps
  several agents in one project from colliding: atomic claims, path and resource
  scopes held until close, dependencies, capabilities, leases with heartbeat,
  stale-revision detection, required evidence, review and rework, a store shared
  by every git worktree, and a generated board. `SkillForge_Agent_Kit.yaml`
  builds its release.

### Changed

- Every project import rejects card IDs that duplicate another domain's; a
  project only carries its own domain, so its validator could not see them.
- The recipe-coverage test derives recipe names from the domains present
  instead of a hand-kept list.
- `validate.py --package` accepts an existing package that has modules but no
  cards yet; a package name that does not exist still fails.
- Module runtime code is `AGPL-3.0-or-later`, like the rest of PASS's code;
  `LICENSE.md` and the generated release notice say so.

## 1.0.0-beta.56 - 2026-09-18

Merged from the writing lane's unattended-dispatch baseline. That archive forked
at beta.51 and numbered its changes beta.52 to beta.55, which collide with the
Unreal entries below; they land here as one release.

### Added

- Single-source unattended runner at `PASS/source.py`. An explicit user
  authorization is persisted for one source through completion. The host still
  performs every substantive PASS read; the runner renders and audits
  preflight/landing packets, consumes routine gates and stops on genuine
  practitioner-required decisions.
- State-driven dispatch: `source.py drive` issues exactly one persisted action
  lease for the current substantive phase, and an unattended `PASS/pass.py`
  submission is rejected unless the lease matches the run state, unit and state
  hash. Consumed leases move to `controller/action-history/`.
- `source.py report` as the only authoritative surface for unattended progress
  and completion claims.
- Source-byte identity recorded right after LOAD, with size- and SHA-256-verified
  `rebind-source` so a run survives a project-chat path change without letting a
  different source inherit it. Final source completion runs full-library schema
  and reference checks.
- Canonical `pass.py present` renderer for preflight and landing packets, with
  every disposition and taxonomy bucket, including empty ones.

### Changed

- A valid preflight now stops at `preflight_accept`: `present` must render the
  packet and `accept-preflight` requires explicit user confirmation bound to its
  SHA-256. The initial request to run PASS is not confirmation. `revise-preflight`
  handles corrections before acceptance.
- Preflight is source-wide and never repeats per unit; `replan` amends the
  accepted remaining plan and is not a new preflight.
- Landing decisions are hash-bound to the rendered packet and no longer
  pre-filled with `user approval`. `approval_required` deltas and
  practitioner-dependent checkpoints remain nondelegable hard stops.
- `close-run` also removes source identity, authorization, audit and completion
  scratch.
- The `pass-authoring` discovery wrappers point unattended hosts at `drive` and
  `report` rather than the lower-level `advance` primitive.
- Workflow test fixtures now pass through the preflight acceptance and landing
  presentation gates, with a test pinning the bound-confirmation rule. The
  archive had not updated them. `CLAUDE.md` and `AGENTS.md` state the new
  authoring rule in shorter prose to stay inside their cold-start budget.

## 1.0.0-beta.55 - 2026-09-18

### Added

- Six Unreal editor cards for ToolMenus ownership and startup, validated camera
  bookmark exchange, persistent toolbar publication and observable qualification
  Drills. Completed the fifth editor-book unit through both full reads,
  standalone card review and verified landing with the existing book preflight.

### Changed

- Refine command routing with cheap availability predicates, execution-time
  validation and measured cache/invalidation decisions. Clipboard and visible
  toolbar qualification remain distinct from native camera/menu checks.

## 1.0.0-beta.54 - 2026-09-18

### Added

- Ten Unreal editor cards for explicit world scope, actor placement/update,
  batched selection notifications, toolkit state, context-menu lifetimes,
  shared/local configuration and requirements-based mode selection. Completed
  the fourth editor-book unit through both full reads, standalone card review
  and verified landing with the existing book preflight.

### Changed

- Refine the Unreal transaction Pattern with creation-container and selection
  storage ownership, batched changes and explicit partial-failure reporting.
  Native actor-operation checks remain separate from future toolkit UI
  qualification and learner training.

## 1.0.0-beta.53 - 2026-09-18

### Added

- Four Unreal editor cards for explicit selection policies, validated asset
  reimport, ordered reimport execution and observed-outcome practice. Completed
  the third editor-book unit through both full reads, standalone card review
  and verified landing with the existing book preflight.

### Changed

- Refine the Unreal command-routing Pattern with scoped callbacks, weak-list
  checks, receiver teardown, input phases/repeats and intentional rejection
  behavior. Engine implementation checks remain separate from learner training.

## 1.0.0-beta.52 - 2026-09-18

### Added

- Dedicated `software-engineering/unreal-engine` module with editor Patterns,
  Action Protocols and Drills for module boundaries, mode/style lifetimes,
  command routing, borrowed UObject selections, explicit feedback and reversible
  material edits. Eleven cards completed through the executable authoring run.
- Include the Unreal Engine module and its core prerequisites in the canonical
  Software Engineering skill recipe. General C++ instruction remains in its
  existing language module.

### Changed

- Drill-discovery checks include the Unreal module and compare the discovered
  identities against the library rather than a fixed historical drill count.

## 1.0.0-beta.51 - 2026-09-18

### Added

- Supported `PASS/pass.py` entrypoint for ordinary source authoring: canonical
  LOAD, authorized existing-domain selection, structural preflight, one active
  instructional unit, consequential-question checkpoints, full PASS 1 and cold
  PASS 2 declarations, exclusive reasoned dispositions, and hash-bound card-only
  PASS 3 before verified unit landing. Unsupported curriculum-audit progression
  fails closed.
- Disposable book/run workspaces under `workspace/skill-staging/<domain>/<book-run>/`
  with canonical category paths for drafts. Validation overlays replace live
  owners, check schema/assets/changed-card relations and staged recipe closure,
  and check library-wide IDs at integration. Landing regenerates indexes,
  verifies bytes, restores files on ordinary write failure, rejects stale live
  reviews, removes integrated drafts, and advances exactly one unit without a
  Git commit. Instructional replanning preserves closed units.

### Changed

- Route source-authoring discovery through the executable entrypoint while
  preserving `PASS_RUN.md` as human-readable rules. The old stateless preflight
  helper validates forecasts only. Explicitly distinguish temporary controller
  scratch from retired permanent authoring infrastructure.
- Exclude asset README files from preflight card discovery, matching the library
  validator. Preserve all domain cards, Art Stage semantics, image links, and the
  separate SkillForge Code Apprenticeship runtime.

## 1.0.0-beta.50 - 2026-09-17

### Changed

- Require project archives directly in `workspace/project-releases/PASS-project-<domain>.zip`
  under the PASS root, without version subfolders unless requested. Keep finished
  skill ZIPs in the SkillForge repository. Route both agent entrypoints and the
  portable authoring skill to the canonical maintainer destination rules.

## 1.0.0-beta.49 - 2026-09-17

### Added

- Stateless ordinary-authoring preflight controller with exact record fields,
  contiguous unit IDs, explicit card-potential forecasts, and overlap resolution
  against the active domain's live cards. The repository test suite includes its
  gate checks and malformed-input regressions.

### Changed

- Merged tested authoring doctrine: canonical-instruction load gate, provisional
  first-read cards and secondary-subject flags, full second rereads with exclusive
  reasoned dispositions, semantic and identity checks on the third card read,
  completion stamps, explicit empty delta buckets, and reasoned taxonomy changes.
  Only preflight is currently Python-enforced; the three reads remain model
  procedure.
- Converted all 17 Art PNG reference assets to JPEG at quality 90, retaining
  dimensions, asset review sidecars, and the frozen Art Stage instructions.
  Updated asset links and format-dependent checks. Reference image bytes fell
  from 23,504,899 to 7,656,950 (67.4 percent smaller).

## 1.0.0-beta.48 - 2026-09-17

### Removed

- Reverted 1.0.0-beta.45 and 1.0.0-beta.47 in full: the `languages/python` module
  and its two cards, its release-recipe, runtime-profile and skill-description
  registration, and every software-engineering core card and Drill edit from the
  *Beyond the Basic Stuff with Python* run. The run skipped the second source read
  and the third card read that `PASS/docs/PASS_RUN.md` section 2 requires, so none
  of its output is trusted.

## 1.0.0-beta.47 - 2026-09-16

### Added

- A `software-engineering/languages/python` module, registered in the Software
  Engineering release recipe, runtime profile and skill descriptions. The runtime
  profile honors a project's declared `requires-python` and otherwise targets the
  current stable CPython.
- Two Python cards, checked on CPython 3.14.7: keeping names off built-ins and
  importable modules (including a local file that breaks a standard-library import),
  and testing a missing value with `is None` rather than truthiness.

### Changed

- Core cards checked against Python from *Beyond the Basic Stuff with Python*
  chapters 3 to 6 no longer assume a compiler where the decision does not need one:
  coding style, layout, name length, dedicated types, time types, the ambiguous-choice
  card, exhaustive enum handling and its Drill, writing in the language you are in,
  and the multi-way decision Action Protocol.
- Narrowed false universal claims: a dedicated type does not stop positional
  arguments being swapped at construction; parentheses change the meaning of a
  comparison chain where chains have their own meaning; a global is aliased through a
  parameter only by reference or in-place mutation; a flag required by name states
  its direction.
- Added to core: blank lines as the layout choice a formatter leaves to you, units
  in names when no type carries them, requiring arguments by name where the language
  can, naming compared string values, not sharing one constant between coinciding
  meanings, and stubs that fail when called.

## 1.0.0-beta.46 - 2026-09-16

### Changed

- Require relevant language-agnostic Software Engineering core Patterns, APs and
  Drills to be reviewed against each new or extended language module's instructional
  books and cards, with target-version/toolchain checks for executable claims.
  Keep one shared core owner; distinguish authoring review from empirical qualification.
- Require workspace files to use existing purpose buckets and task-owned directories.
  Verify durable integration or completion before removing owned scratch and staging
  copies; protect original inputs, other tasks and explicit evidence holds. Route
  these rules through both agent entrypoints, portable authoring and runtime instructions.

### Added

- Focused regression checks for the language-book/core review gate, workspace lifecycle
  and instruction routing. No automatic cleanup or apprenticeship-controller change.

## 1.0.0-beta.45 - 2026-09-16

### Changed

- The software-engineering warnings card now covers every tool that checks code, not
  only the compiler: a language without a compile step gets these checks from a
  linter or type checker that must run in the build, and some toolchains hide whole
  warning categories unless switched on. The error-signalling Action Protocol's
  warning step now says the same.
- The defect-finding Action Protocol no longer assumes a memory-unsafe language when
  listing causes of intermittent failures: it adds orders the language does not
  promise, such as hashed-collection iteration order, and keeps uninitialized reads
  and use-after-free for languages that allow them.

### Fixed

- Two core cards stated false Python facts as examples (variadic arguments arriving
  as a list, and integers being stored by value). Both examples are now written
  without depending on one language, and the negative-transfer card's
  uninitialized-variable example is stated precisely.

## 1.0.0-beta.44 - 2026-09-16

### Fixed

- Repaired all 318 Writing card IDs to match their type-prefixed filename stems,
  including foundation links, cross-links, and references within card bodies.
  Card teaching content and placement are preserved.
- Updated dependent documentation examples, test fixtures, and current Writing
  memory owner references to the repaired IDs; training history is preserved.

## 1.0.0-beta.43 - 2026-09-16

### Added

- One software-engineering core problem-solving card from Fomin and Kratsch: splitting
  the choices in half and matching the two lists (meet in the middle).

### Changed

- The pruning card now says to branch on the decision with the fewest remaining options,
  with measured search-tree sizes.
- The table-or-memoise card now covers splitting the answer at its middle when no table
  fits, with measured time and memory.

## 1.0.0-beta.42 - 2026-09-16

### Changed

- The work-and-span card no longer claims that processors beyond the work/span ratio
  buy nothing: it separates the ratio (the speedup ceiling) from the widest level (the
  processor count that reaches it), with measured speedups from simulated task graphs.
- The dependency-classification card now asks for a schedule before a loop nest with a
  true dependency is called sequential, with measured anti-diagonal and tiled runs.

## 1.0.0-beta.41 - 2026-09-16

### Added

- One software-engineering core problem-solving card from Sedgewick and Flajolet,
  chapter 9: finding where an iterated function repeats with two copies at different
  speeds, in constant memory.

### Changed

- The collision-scheme card now carries measured probe counts for stepping to the next
  slot and for a key-computed step at 50% to 99% occupancy.

## 1.0.0-beta.40 - 2026-09-16

### Added

- Two software-engineering core cards from Sedgewick and Flajolet, chapters 6 to 8:
  sorting a compact order instead of large records and applying it once by cycles,
  and resuming a failed pattern match where what it read still allows.

### Changed

- The counted cost-model card now states the input model on what a method receives,
  not on the structures it builds.

## 1.0.0-beta.39 - 2026-09-16

### Added

- One software-engineering core performance card from Sedgewick and Flajolet,
  chapters 1 to 4: predicting cost from counted operations and measured unit costs,
  for absolute figures and same-growth comparisons that a growth estimate cannot
  answer.

## 1.0.0-beta.38 - 2026-09-16

### Fixed

- Code Apprenticeship schema v4 defaults review forms to same-reader, requires
  declared separate auditor/grader roles for every valid study, and explicitly
  reports that the controller cannot verify actual context isolation. Portable
  Software Engineering instructions require fresh reviewers and an external
  administrator when the implementer's host cannot provide them.
- Evidence locations reject blank-only ranges. Metadata and every improvement
  check require machine-output evidence, not implementation snippets alone.
- New studies pin the controller implementation fingerprint and fail closed if
  it changes. Schema-v2/v3 records remain status-readable and otherwise read-only;
  old studies, cards, memory, and the stopped burn-in batch are preserved.
- Negative-case regression tests cover premature craft grading, frozen work/audit
  tampering, invalid evidence, missing machine-output locations, false default
  separation, and changed controller fingerprints. Canary and authorized-batch
  stopping guidance no longer imply that green transitions prove rejection checks.

## 1.0.0-beta.37 - 2026-09-16

### Added

- Three software-engineering core cards that close the CLRS run (chapters 16, 25,
  29 and 31): searching only a form every solution can be rearranged into;
  deciding with a random test whose error shrinks with each trial; and composing an
  associative step by doubling.

### Changed

- Two refinements from CLRS chapters 33 and 35: the cheapest exact geometric
  predicate uses only additions, subtractions and multiplications; an approximation
  ratio is proved against a computable bound the optimum cannot beat, and that bound
  per instance is a ceiling on the gap.
## 1.0.0-beta.36 - 2026-09-16

### Added

- Two software-engineering core cards from CLRS chapters 24, 25 and 28: choosing
  a shortest-path method by whether the network can have cycles and negative
  costs (including all-pairs choice by density and one-time cost adjustment), and
  solving a linear system by factoring with row exchanges rather than by inverting.

### Changed

- One problem-solving refinement from CLRS chapter 26: whole-number capacities
  give whole-number flows, so one-to-one assignment reduces to flow without paying
  for the whole-number requirement.
## 1.0.0-beta.35 - 2026-09-16

### Added

- Six software-engineering core cards from CLRS chapters 6, 12, 13, 18, 19, 21
  and 22: saying which outside references survive each operation; keeping a
  structural invariant loose enough to repair locally; repairing on the way down
  so one pass never backs up; sizing each node to one transfer of the slow tier;
  merging groups by linking representatives rather than relabeling members; and
  ordering dependent work by its graph while naming the cycles.

### Changed

- Two performance refinements from CLRS chapters 19 and 20: defer tidying to the
  operation that traverses the untidy part anyway; the comparison bound and its
  key-property escape extend from sorting to priority queues.

## 1.0.0-beta.34 - 2026-09-16

### Added

- Two software-engineering core performance cards from CLRS chapters 8 and 9:
  asking for the least order the consumer needs (selection instead of a full
  sort), and sorting by key values once a comparison sort is the measured cost.
  The first becomes the foundation of the C++ weakest-ordering-operation card.

### Changed

- Three problem-solving refinements from CLRS chapters 4, 7 and 15: find a
  recursion's hand-off size by measuring on the target machine; randomized
  partitioning does not rescue repeated keys or survive an observing adversary;
  optimal parts must compose into a legal whole, and a frontier-only table cannot
  reconstruct the answer.

## 1.0.0-beta.33 - 2026-09-16

### Changed

- C++ currency pass closed: all nine C++ Action Protocols and seventeen Drills
  read. The const-correctness Action Protocol and Drill now follow their owner's
  C++23 form — one member with a deduced explicit object parameter — and keep
  const delegation as the C++20 spelling.

## 1.0.0-beta.32 - 2026-09-16

### Changed

- C++ currency batch 7: six cards connect their decision to a C++20 or C++23
  facility — `try_emplace` beside plain emplacement, deducing `this` in place of
  const delegation, `constinit` for a static others depend on, a returned view as
  a handle to internals, `std::generator`, and `std::bit_cast` with
  `std::to_underlying`.

### Fixed

- The emplacement card no longer states that an associative container always
  constructs a rejected duplicate; whether it does is implementation-dependent.

## 1.0.0-beta.31 - 2026-09-16

### Changed

- C++ currency batches 2 to 6: seven cards connect their decision to a C++11, C++20
  or C++23 facility — moving the base and members in a hand-written move,
  surviving self-move assignment, `std::out_ptr` for output-parameter acquisition
  and pointer-to-pointer interfaces, `std::ranges::swap`, `std::reference_wrapper`
  for an always-present but retargeted referent, and `consteval` beside
  `constexpr`.

### Fixed

- `PAT_use_private_inheritance_judiciously` no longer claims composition cannot
  obtain the empty-base size saving. Under C++20 a member marked
  `[[no_unique_address]]` may take no storage; the card now records that MSVC
  honours only its vendor spelling of the attribute.

## 1.0.0-beta.30 - 2026-09-16

### Changed

- Two more C++ Patterns connect their decision to the C++20 range algorithms.
  `PAT_match_the_search_comparison_to_the_sort_comparison` now warns that a
  matching comparison with a different projection still searches under a
  different ordering; `PAT_write_a_missing_algorithm_in_the_librarys_own_shape`
  now lets the end take its own type and the convenience overload accept any
  range, so the shape reaches views that end on a sentinel.

## 1.0.0-beta.29 - 2026-09-16

### Changed

- Three C++ Patterns now connect the decision they teach to the language feature
  that later arrived to express or check it. `PAT_lift_each_varying_design_decision_to_a_parameter`
  points at stating a parameter's required expressions as a checked constraint;
  `PAT_make_a_predicate_a_pure_function` extends the purity requirement to range
  projections; `PAT_prefer_range_member_functions_to_repeated_single_element_calls`
  names the container members that take a range directly.

## 1.0.0-beta.28 - 2026-09-16

### Changed

- Software Code Apprenticeship schema v3 replaces self-attested evidence booleans
  with source-line facts, an unresolved-context ledger, an exact source-to-fixture
  reproduction map, property-sensitive comparison checks, and separate project
  and fixture toolchain metadata.
- Evidence auditing now precedes and gates craft grading. Schema-v2 studies remain
  available through `status` but are read-only, so old results cannot be finalized
  under the stronger contract.
- Studies now distinguish held-out validation from motivating-example regression
  and exploration. Only held-out validation can export a candidate Skillset Memory
  event; reusing the source that motivated a repair cannot validate that repair.

### Tests

- Replaced generic all-green controller fixtures with adversarial coverage for
  unsupported card conditions, incomplete reproduction maps, nondiscriminating
  comparisons, fixture-toolchain omissions, source-context invalidation, and
  circular motivating examples.

## 1.0.0-beta.27 - 2026-09-15

### Added

- Four Software Engineering Patterns extracted from Cormen/Leiserson/Rivest/
  Stein, covering amortized reasoning over a sequence of operations, choosing a
  hash table's collision scheme by whether keys are deleted, selecting a stored
  derived value by how far its updates propagate, and parallelising the combine
  step of a recursive algorithm so it does not become the critical path.

### Changed

- `PAT_estimate_the_order_before_you_run_it` now warns that the worst case is
  frequently the routine case rather than an exotic one, since a lookup that
  finds nothing must examine every candidate.
- `PAT_sample_a_split_point_you_cannot_afford_to_compute` now reaches the case
  where there is no expensive parameter, only an input order you were about to
  assume was benign, and warns that a hand-written shuffle is easily biased.

## 1.0.0-beta.26 - 2026-09-15

### Changed

- Project handoffs under `workspace/handoffs/` are local again and no longer
  tracked. The workspace allowlist keeps reusable tools and canonical release
  recipes; everything else, handoffs included, stays on the machine that owns
  it. The five handoff files remain on disk and were removed from the index
  only.

## 1.0.0-beta.25 - 2026-09-15

### Added

- Added the portable Software Code Apprenticeship controller. It freezes a
  source-first reconstruction of one bounded human-code slice before exposing an
  exact Pattern/AP bundle, then requires an implemented PASS-guided alternative,
  equivalent machine evidence, and a closed comparison outcome.
- Reusable coding habits now leave the controller as structured candidates with
  an observation, adoption rule, verification method, and explicit disposition;
  they are never silently promoted from one codebase into canon or memory.
- Code Apprenticeship grades distinguish whether PASS improved the design, the
  human design remains preferable, the choices serve different constraints, or
  they are equivalent. Qualification remains PASS/FAIL/INVALID and cannot be
  decided by style preference, line counts, or another proxy.
- Code Apprenticeship grades now fail closed unless the card condition is backed
  by deciding source declarations, the source context is complete, the
  reproduction preserves those facts, the claimed improvement is exercised,
  and revision/language/toolchain metadata matches the evidence. Neutral corpus
  runs reject floating revisions such as `main` and `master`.
- Software Engineering releases now vendor the controller and declare it in
  release-manifest schema 3. Finalization exports a reviewable
  `software-card-field-test` history candidate without editing cards or Skillset
  Memory.

### Changed

- The software field-test protocol now has three explicit passes: human-design
  discovery, card qualification, and PASS-guided improvement. Human precedent is
  neither treated as infallible nor merely imitated; the agent must preserve the
  real contract and test whether PASS can improve a named engineering property.

## 1.0.0-beta.24 - 2026-09-15

### Added

- The learner-neutral Drill runner now supports human or AI baseline, teaching practice, isolation,
  retention, and transfer sittings. Each sitting is independently frozen, later measurements require
  novel scenarios, and a neutral profile treats model identity as optional reproducibility metadata.
- Practice can teach through Drill Instructions, an exact same-domain/metaskills Pattern/AP bundle,
  external material, or a declared combination. Stage practice is therefore both usable training and
  evidence about whether the teaching material works.
- A linked training sequence keeps the learner and runtime profile stable; the teaching intervention
  changes, not the human, model, host, or recorded settings.
- Non-passing criteria carry a provisional application or exposed-skillcard cause plus a transferable
  mistake, correction, and prevention lesson. The runner rejects named-human or named-model weakness
  profiles.
- Append-only history now supports factual `metadata_correction` events and `evidence_correction`
  events that quarantine invalid evidence without deleting it.

### Changed

- Card qualification is now key-blind and skillcard-present. The runner automatically packages each
  Drill's exact linked Patterns and APs while keeping Success Check and Common Failures hidden until
  the answer is frozen. A cut before Instructions tests the linked cards; a cut before Success Check
  tests the Drill-led bundle.
- Pattern, AP, and Drill IDs are resolved from card front matter rather than from naming prefixes, so
  the same runner works with semantic IDs used by Art, Writing, and other skillsets.
- Drill events now state the stabilization purpose `skillset-improvement`: model or human metadata
  reproduces the conditions, while compact Skillset Memory retains transferable lessons about the
  skillset rather than a learner profile. Persistent model memory remains a separate future system.
- Software card field tests keep using bounded slices of real human code to test whether Patterns and
  APs guide real engineering work, without claiming that a model changed.

### Fixed

- Qualification is closed-result: every criterion is PASS or FAIL, the overall result is derived from
  those criteria, and a setup, tool, contamination, or package failure is INVALID. `partial` and
  craft grades on invalid sittings are rejected.
- A qualification or practice sitting can no longer claim isolation, retention, or transfer, and a
  single sitting cannot claim that the skill caused its result.
- Historical events `SE_EV_0081` through `SE_EV_0110` are preserved but quarantined by append-only
  corrections. The currency-maintenance events remain card-review history, and the Bionic sittings
  retain their Drill/compiler observations and accepted repairs; neither batch now counts as learner
  improvement, isolation evidence, Pattern/AP qualification, or named-model weakness. Their former
  partial outcomes are retrospectively disposed as PASS, FAIL, INVALID, or not applicable.

## 1.0.0-beta.23 - 2026-09-14

### Fixed

- `DRILL_redesign_interface_to_prevent_misuse` now asks for the scoped-enumeration attempt in a step of
  its own, before Month is constrained with predefined objects: record whether the enumeration fixes
  the argument order and refuses a plain integer, then cast an out-of-range integer to it and record
  what the result holds. The Success Check already graded that an explicit cast still yields an
  undeclared value, but no step asked for a cast, so whether a run tried one was left to chance.
- The same Drill's invalid-month bullet now requires the compiler's rejection to be recorded, so a
  predicted rejection no longer passes.

### Changed

- Recorded four blind C++ Drill sittings in software-engineering Skillset Memory as training events
  `SE_EV_0107` to `SE_EV_0110`, all valid. Three confirm earlier repairs in practice: the
  derived-class copying functions Drill (beta.21), the copy-assignment destruction step (beta.21), and
  the per-argument braced call in the interface Drill (beta.22). The fourth is a valid rerun of the
  pimpl sitting recorded invalid in beta.22.

## 1.0.0-beta.22 - 2026-09-14

### Fixed

- `DRILL_redesign_interface_to_prevent_misuse` now asks for a wrong-order call with each argument in
  its own braces, such as `Date({30}, {3}, {1995})`, in its Instruction, Success Check and Common
  Failures. "A braced call in the wrong order" also reads as `Date{30, 3, 1995}`, which aggregate
  wrappers reject, so a run following that reading never saw the aggregate hole the check exists to
  expose. `PAT_make_interfaces_hard_to_misuse` names the same per-argument form and notes that bracing
  the whole argument list is refused.

### Changed

- Recorded eight more blind C++ Drill sittings in software-engineering Skillset Memory as training
  events `SE_EV_0098` to `SE_EV_0104` and `SE_EV_0106`. Six are valid; `SE_EV_0104` (the abandoned
  interface-01 sitting) and `SE_EV_0106` are recorded invalid for harness failures (an engine
  auto-update that stalled generation, and a shell tool that could not run commands) and count toward
  nothing.
- Added `SE_EV_0105`, which corrects the taker setup recorded in `SE_EV_0089` to `SE_EV_0097`: those
  sittings ran the Q4_K_M model file with its vision projector, not Q5_K_M. Training history is
  append-oriented, so the original events are left as written.

## 1.0.0-beta.21 - 2026-09-13

### Fixed

- `DRILL_complete_a_derived_class_copying_functions` no longer asks for two incompatible base
  classes. Its base-member step needed a base with hand-written copying functions, while its move
  bullet needed one whose moves were generated, so one of the two could not be met. The Practice Task
  now states that `Customer`'s copying and moving functions are compiler-generated, and the added
  member goes on the derived class, whose hand-written copying functions the compiler never reports
  as stale.
- `DRILL_make_copy_assignment_self_and_exception_safe` now asks what happens when the target is
  destroyed after the throwing copy. Its Success Check grades the naive version's destructor freeing
  released memory a second time, but reading the target's state is itself a use-after-free that stops
  an AddressSanitizer build before the destructor runs.

### Changed

- Recorded eight blind sittings of C++ Drills in software-engineering Skillset Memory as training
  events `SE_EV_0090` to `SE_EV_0097`. A local model took each Drill cut before its Success Check,
  and the grader rebuilt and reran every answer and checked the Drill's claims with its own programs.
  Seven sittings are valid, all partial passes; `SE_EV_0091` is recorded invalid because its session
  reused an earlier sitting's context, and `SE_EV_0092` is its clean rerun.

## 1.0.0-beta.20 - 2026-09-13

### Changed

- Recorded the first blind sitting of an updated C++ Drill in software-engineering Skillset
  Memory as training event `SE_EV_0089`. A local model took
  `DRILL_fix_templatized_base_class_name_access` cut before its Success Check, and the grader
  rebuilt and reran every answer. The sitting passed all six criteria. It also flagged a possible
  Instructions gap: bullet 4's stated reason is not asked for by its own step. No card changed.

## 1.0.0-beta.19 - 2026-09-13

### Fixed

- APs are called Action Protocols everywhere, as `PASS/docs/PASS_DOCTRINE.md` defines them. The
  README said "ordered action procedures", two core readability cards said "the naming action
  plan", and a Skillset Memory entry and three training events said "Action Pattern".
- `PAT_recover_the_iterator_from_erase_rather_than_advancing_it` leads with C++20 `std::erase_if`,
  which covers every standard container, and `std::erase`, which covers the sequence containers and
  strings, and keeps the member erase by key for ordered associative containers.
  `PAT_remember_an_algorithm_cannot_change_a_containers_size` states each function's coverage and
  returned count, and `AP_settle_a_containers_contract_before_filling_it` delegates to them first.

## 1.0.0-beta.18 - 2026-09-13

### Fixed

- Updated all nine C++ Action Protocols against the patterns they activate, after the pattern
  sweep and the Drill update changed several of those owners. No step order, gate, or branch
  changed; step summaries that restated an owner's old claim were corrected.
- `AP_make_a_function_exception_safe` no longer says a function committing to a basic-only callee
  cannot offer the strong guarantee: doing the work on a copy or making it reversible can. It adds
  the reordering route and the `noexcept` completion check.
- `AP_write_copy_control_for_a_resource_owning_class` starts from the Rule of Zero, defaults moves
  only where every member empties its source, and no longer calls copy-and-swap the one
  construction giving both self-assignment safety and the strong guarantee - copy-first ordering
  does for a single resource.
- `AP_give_an_acquired_resource_an_owner` gives the current make-function reasons and exceptions,
  the four current ownership options, and the named-owner check.
- `AP_replace_new_and_delete_for_a_named_reason` no longer calls a missing placement delete
  silent at build time, and verifies arrays of the class.
- `AP_make_a_class_const_correct` prices an embedded mutex, notes that the reverse delegation
  compiles silently, and checks writes through pointer members.
- `AP_choose_the_relationship_between_two_types` checks that composition forwards nothing that
  reopens the invariant.
- `AP_design_a_customization_point` limits locking in a wrapper to a closed override set and
  aligns its default-argument check with its owner.
- `AP_settle_a_containers_contract_before_filling_it` no longer says removing elements never
  returns memory: contiguous containers keep their capacity, node-based ones free erased nodes.
- `AP_make_shared_state_safe_in_cpp` adds the static-mutex and single-acquisition-order
  obligations to its lock route.

## 1.0.0-beta.17 - 2026-09-13

### Changed

- Updated the last four C++ Drills - interface-design, inheritance, virtual-functions and
  concurrency - against their compile-swept patterns, completing the currency update of all 17 C++
  Drills.
- `DRILL_redesign_interface_to_prevent_misuse` builds the wrapper types three ways, since only
  `explicit` constructors reject both the raw and the braced transposed call, and compares the
  design with C++20's `std::chrono::month`.
- `DRILL_refactor_broken_is_a_to_composition` narrows to `Set` over `std::list` and adds forwarded
  iterators, since a mutable one lets clients write a duplicate.
- `DRILL_apply_the_nvi_idiom` moves the lock rule and the cost list out of its Instructions.
- `DRILL_restructure_a_class_that_locks_every_member` runs the nested acquisition and the
  per-object guard over static state, and accepts one `std::scoped_lock` over both mutexes.
- `PAT_make_interfaces_hard_to_misuse` notes the standard calendar types' choice of explicit
  construction plus a validity query.
- Removed book item numbers from the Drills' Notes.

### Fixed

- `PAT_lock_at_the_public_boundary_and_nowhere_inside` no longer says a nested ordinary-mutex
  acquisition deadlocks in practice: it is undefined behaviour, and one mainstream implementation
  threw `std::system_error` in every build mode measured. The Drill's matching wording follows.

## 1.0.0-beta.16 - 2026-09-13

### Changed

- Updated four more C++ Drills in memory-management, templates and traits against their
  compile-swept patterns, with every claim the new text makes compiled first.
- `DRILL_write_a_conforming_operator_new` runs the failure path through the class's allocation
  function and adds arrays, which reach the global array operator new and bypass the class's
  scalar forms.
- `DRILL_pair_a_placement_new_with_placement_delete` builds a near-match placement delete, which
  compiles, is never called, and draws the same warning as a missing one; adds the buffer placement
  form to the hidden forms; and compiles the ordinary delete with the normal form removed.
- `DRILL_fix_templatized_base_class_name_access` observes dispatch through each fix, requires a
  conforming compiler mode, builds the missing-specialization timing both ways, and adds the
  unqualified call that silently binds to a same-named namespace-scope function.
- `DRILL_implement_traits_based_dispatch` adds a forward-only iterator and the `std::views::iota`
  iterator, which classic tag dispatch steps one at a time and C++20 concept dispatch advances with
  `+=`; requires the runtime-`if` failure to be compiled; and records the ambiguity with
  `std::advance`.
- `PAT_access_templatized_base_members_explicitly` warns that an unqualified call can compile by
  binding to a same-named function outside the class.
- Removed book item numbers from the Drills' Notes.

## 1.0.0-beta.15 - 2026-09-13

### Changed

- Updated four more C++ Drills against their compile-swept patterns, with every claim the new
  text makes compiled first.
- `DRILL_convert_a_class_to_the_pimpl_idiom` covers copy and move: declaring only the destructor
  leaves the handle neither copyable nor movable, and moves defaulted in the header fail at the
  client. It also records the moved-from state and the const write that the bare handle permits.
- `DRILL_implement_nonthrowing_swap_for_pimpl` measures the standard swap first: with `noexcept`
  moves it copies and allocates nothing, so the custom swap is argued as a primitive rather than a
  speedup. It adds the qualified `std::swap` call that bypasses the customization.
- `DRILL_add_const_correctness_to_a_class` compiles the reverse delegation, which nothing stops,
  and prices a thread-safe cache: a `mutable` mutex removes copy and move.
- `DRILL_convert_constructor_assignment_to_init_list` adds default member initializers across two
  constructors, counts the construction work, and builds an initializer that reads a later member.
- `PAT_minimize_compilation_dependencies` warns that `std::unique_ptr` does not propagate `const`
  and routes const members through a const-qualified accessor.
- Removed book item numbers from the Drills' Notes.

## 1.0.0-beta.14 - 2026-09-13

### Fixed

- `build_release.py` runs its helper scripts with UTF-8 pinned at both ends of the pipe. On
  Windows it decoded their output with the locale codepage, so a release whose card text
  contains a character like a closing curly quote failed its runtime and Drill discovery
  checks with a `UnicodeDecodeError`.
- The tests that run PASS's own Python scripts decode their output as UTF-8, so a Drill name or
  error message quoting card text no longer passes or fails by the locale codepage.

## 1.0.0-beta.13 - 2026-09-13

### Changed

- Updated five C++ Drills in copy-control, resource-management and exception-safety against
  their compile-swept patterns, with every claim the new text makes compiled first.
- `DRILL_make_copy_assignment_self_and_exception_safe` no longer asks the runner to price an
  extra copy in copy-and-swap: counted, copy-first and copy-and-swap each make one allocation
  and one copy, and only in-place assignment saves the allocation. It now requires an
  instrumented build, explains the fixed layout that keeps a raw owner, and ends with the
  `unique_ptr`-member rewrite.
- `DRILL_complete_a_derived_class_copying_functions` measures moves: hand-written copying
  functions turn `std::move` into copies, and removing them restores complete copies and moves.
- `DRILL_choose_copying_behavior_for_an_raii_class` no longer allows defaulted moves on a
  raw-handle guard, which unlock twice; it adds a move-assignment count and the scope-pinned
  option.
- `DRILL_refactor_manual_cleanup_to_raii` names `std::unique_ptr` and moves the handover into
  the factory.
- `DRILL_make_a_function_exception_safe` records the stream position after a failed call, so the
  consumed input is observed rather than asserted, and checks the committing swap is nothrow.
- `PAT_choose_raii_copying_behavior_deliberately` and `AP_write_copy_control_for_a_resource_owning_class`
  add the fourth ownership option, an owner neither copyable nor movable, which `std::lock_guard`
  and `std::scoped_lock` use.
- Removed book item numbers from the five Drills' Notes.

## 1.0.0-beta.12 - 2026-09-12

### Changed

- Repaired sixteen more C++ cards against compiled evidence, completing the topic-by-topic
  sweep of every pattern in the `software-engineering` C++ module across const-correctness,
  parameter-passing, operators, foundations, memory-management and algorithms.
- `PAT_apply_const_to_lock_invariants` no longer says const locals catch `if (a * b = c)`;
  a ref-qualified assignment operator is what refuses it for class types.
- `PAT_return_by_value_when_returning_new_object` says a deleted move fails a named return
  in every build, whether or not the copy is elided.
- `PAT_prefer_pass_by_reference_to_const` says a const reference is reloaded only where an
  intervening write could alias it.
- `PAT_pass_a_smart_pointer_only_to_transfer_ownership` states the extra allocation for the
  control block when a unique pointer becomes a shared one.
- `PAT_implement_the_standalone_operator_from_the_compound` builds the result from a named
  local, since returning the compound expression copies from an lvalue.
- `PAT_leave_the_address_of_operator_alone` notes that the standard library guards itself
  with `std::addressof`; generic code that writes `&x` is where the damage lands.
- `PAT_leave_the_short_circuit_and_comma_operators_alone` notes that one current compiler
  still evaluates free overloads of `&&` and `||` right operand first.
- `PAT_interpose_a_proxy_when_an_operator_cannot_see_its_context` labels multi-argument
  subscripting as C++23 and keeps the C++20 path.
- `PAT_prefer_the_form_that_refuses_what_you_did_not_mean` scopes the `typename`
  requirement under C++20, excepts `bool` from `nullptr`'s conversions, and notes the
  deprecation warning on comparing unrelated enumerations.
- `PAT_do_not_compare_integers_across_signedness` separates casting the signed operand from
  casting the unsigned one.
- `PAT_replace_new_delete_only_with_clear_reason` describes the C++17 split between plain
  and aligned allocation.
- `PAT_pair_placement_new_with_placement_delete` notes that a compiler may warn about the
  missing placement delete.
- `PAT_prefer_make_functions_to_direct_new` says `make_shared` never calls a class's
  allocation functions and points to `std::allocate_shared`.
- `PAT_choose_the_weakest_ordering_operation_that_does_the_job` says `stable_partition`
  requires bidirectional iterators.
- `PAT_match_the_search_comparison_to_the_sort_comparison` and
  `PAT_make_sure_the_destination_range_can_hold_the_output` name the debug-library and
  sanitizer checks that do catch their failures.

### Added

- Updated `software-engineering` memory: distance from C++20 predicts language-rule defects,
  C++14-era sources are not exempt, and a correction should be searched for across the package
  before one card is repaired.

## 1.0.0-beta.11 - 2026-09-12

### Changed

- Repaired four more C++ cards against compiled evidence, continuing the topic-by-topic
  sweep of the `software-engineering` package through iterators and initialization, the
  first of the larger topics.
- `PAT_replace_nonlocal_statics_with_local_statics` no longer tells readers that
  function-local static initialization is not thread-safe, which its own Notes already
  contradicted; sixteen racing threads produced one construction, and only switching the
  compiler's guard off broke it. Its teardown warning now names the right object: the
  hazard is reporting to the object built later, not the one built first.
- `PAT_manually_initialize_builtin_objects` no longer says failed extraction leaves the
  destination unchanged. Since C++11 a failed numeric parse stores zero and an overflow
  stores the limit; only a failure before parsing, such as empty input, leaves it alone.
- `PAT_choose_braces_or_parentheses_deliberately` no longer says braced copy and move are
  diverted to an initializer-list constructor, which a defect resolution applied to C++14
  ended; no longer says an equals sign cannot initialize an uncopyable object, which C++17
  elision changed; and no longer says the general vexing parse draws no warning.
- `PAT_convert_a_reverse_iterator_with_base_and_mind_the_offset` no longer draws an
  implicit conversion from an iterator to a reverse iterator, whose constructor is
  explicit; notes that mainstream libraries give contiguous containers class-type
  iterators, so stepping back from `base()` usually compiles and fails only on pointers;
  and warns that a reference cast can remove an iterator's constness on a library that
  derives one type from the other.

### Added

- Updated `software-engineering` memory: every defect in the first larger topics came from
  a card whose source stands far from C++20, and one card's Notes had already corrected
  advice its own Don't bullet kept giving.

## 1.0.0-beta.10 - 2026-09-12

### Changed

- Repaired four more C++ cards against compiled evidence, continuing the topic-by-topic
  sweep of the `software-engineering` package through interface-design, encapsulation,
  type-deduction, lambdas and coroutines. Every C++ topic holding three patterns or
  fewer is now swept.
- `PAT_make_interfaces_hard_to_misuse` now requires explicit constructors on the wrapper
  types that stop a transposed call, since converting constructors let the raw call
  compile and aggregate wrappers let a braced call in the wrong order compile. It no
  longer recommends const return values, which cost every move of the result; blocking
  assignment to a temporary goes through ref-qualified assignment instead. It no longer
  says every standard container has `size()`, which the singly linked list does not.
- `PAT_expect_one_keyword_to_convert_the_whole_function` lists three coroutine triggers,
  not four: the range-based `for co_await` belonged to the Coroutines TS, was not adopted
  into C++20, and a current compiler refuses it. It also says by-value parameters are
  moved into the frame rather than copied.
- `PAT_decide_where_a_coroutine_suspends_and_who_destroys_it` includes access to the
  promise object in the handle's interface, which is how every result is read.
- `PAT_name_every_lambda_capture` no longer says an empty capture clause certifies that a
  closure depends on nothing outside itself. The compiler checks local variables that
  would need capturing; globals, statics and read-only local constants stay reachable.

### Added

- Updated `software-engineering` memory: every language-rule defect in the last three
  batches came from a source standing far from C++20, older or pre-standard, while cards
  from a C++11/14-era source held every rule.

## 1.0.0-beta.9 - 2026-09-12

### Changed

- Repaired three more C++ cards against compiled evidence, continuing the topic-by-topic
  sweep of the `software-engineering` package. Fifteen further objects were probed: the
  last nine patterns in the one- and two-pattern topics, and the whole of `casting` and
  `construction`. Every C++ topic holding fewer than three patterns is now swept.
- `PAT_cross_a_c_boundary_with_only_what_c_can_express` no longer rules out every base
  class on a struct that crosses into C. Measured, an empty base left the size, member
  offsets and standard-layout answer identical to the plain struct; a base declaring data
  of its own is the case that breaks layout, and the checklist now asks about that.
- `PAT_dont_add_a_default_constructor_a_class_cannot_honor` no longer says a heap array
  cannot take per-element constructor arguments. Since C++11 it takes the same initializer
  as a non-heap array and can take its length from it; only a heap array whose length is
  decided at run time still needs an array of pointers or in-place construction.
- `PAT_restrict_a_special_member_to_control_where_objects_can_exist` now says a
  non-public allocation function discourages heap objects rather than preventing them:
  the array form, a global-scope new, and allocator-based factories and containers all
  compiled past it. It also advises giving a restricted constructor a body, because one
  compiler let a private defaulted constructor through aggregate braces; states the
  address-comparison heuristic's failure as layout-dependent, since on a 64-bit target it
  misclassified heap objects rather than statics; and notes that a constant-initialized,
  trivially destructible local static costs no first-use check.

### Added

- Updated `software-engineering` memory: the observation that claims about what the
  language requires had held without exception no longer stands. Two of the latest
  batch's defects were language-rule claims, both from cards drawn from a pre-C++11
  source, so a card from such a source deserves a probe of its rules as well as of its
  illustrations.

## 1.0.0-beta.8 - 2026-09-12

### Changed

- Repaired four more C++ cards against compiled evidence, continuing the topic-by-topic
  sweep of the `software-engineering` package. Twenty-five further objects were probed
  across virtual-functions, copy-control, inheritance, exception-safety and three of the
  smaller topics; two of those topics needed no repair at all.
- `PAT_price_virtual_dispatch_against_the_real_alternative` no longer quotes the figures
  its own Don't clause forbids, and no longer ranks a tag-and-switch below virtual
  dispatch. Measured at three cases with data access held equal, the switch won by a
  factor of two; the maintenance objection, which holds whichever way a measurement goes,
  is now the stated reason to refuse it anyway.
- `PAT_order_type_dispatch_most_derived_first` now distinguishes the form the language
  knows about, where a current compiler does report a shadowed handler by name, from the
  hand-written table and type-test chain, which get no diagnostic at any warning level and
  are therefore where the ordering has to be maintained deliberately.
- `PAT_treat_undefined_behavior_as_a_whole_program_assumption` now presents its optimizer
  illustrations as entitlements rather than outcomes, because a current compiler at its
  usual optimization level takes neither of them - which is the card's own reason for
  saying that code working today is not evidence. Its sanitizer advice now says to check
  whether the toolchain has one.
- `PAT_choose_index_types_the_compiler_can_assume_do_not_wrap` keeps its codegen
  explanation, which reproduced exactly, and drops the carried claim that the change made
  a sort several times faster: measured, three index types came within three parts in a
  thousand of each other.
- `PAT_prefer_const_and_enum_to_define` no longer predicts what a compiler error will say.
  The durable point is that a `#define` leaves nothing for a diagnostic, a debugger, or a
  linker to name.

### Added

- Added `software-engineering` memory entries recording which kinds of card claim survive
  testing: claims about what the language requires have held without exception across ten
  topics, while every defect found has been a claim about what a compiler reports, what a
  platform measures, that two cases behave alike, or that a tool is available.

## 1.0.0-beta.7 - 2026-09-12

### Changed

- Repaired ten C++ cards against compiled evidence, from a topic-by-topic sweep of
  the `software-engineering` package that tests each card's claims by compiling what
  it prescribes, compiling what it says must fail, and measuring what it quantifies.
  Seventy objects across seven topics were probed; the ten below were the cards whose
  claims did not survive.
- `PAT_return_values_without_top_level_const` now states that ref-qualifying one
  overload of a name obliges every overload of that name to carry a ref-qualifier,
  and that the `const &` form still binds a prvalue so existing reads keep compiling.
  Applied as previously written, the advice did not compile on the ordinary
  mutable/const accessor pair.
- `PAT_do_not_emulate_class_specific_new_handler_with_global_state` now requires a
  local policy's bookkeeping to live in the pool or memory resource every allocator
  instance points at, because per-instance accounting breaks the allocator equality
  contract that lets a container release through any equal instance.
- `PAT_choose_a_thread_safe_initialization_mechanism` no longer carries one
  platform's benchmark ratios as durable guidance. What transfers - the
  order-of-magnitude cost of guarding every access, and the reason to prefer the
  function-local static - is kept; the ratios, which inverted on a supported target,
  are not.
- `PAT_choose_the_execution_policy_the_loop_body_can_survive` no longer implies a
  sequence-length crossover threshold. Per-element work decides, and a length
  threshold measured with one weight of work says nothing about another.
- `PAT_manage_resources_with_raii_objects` now distinguishes the three outcomes of
  dropping a manager's name: a braced or cast temporary releases immediately, while
  the parenthesized spelling is a declaration that either fails to compile or
  silently constructs an owner of nothing.
- `PAT_avoid_overloading_on_universal_references` now separates the base-class case
  from the derived-class case, which is broader: a hand-written derived copy or move
  constructor has both hijacked, including the const copy that was safe in the base,
  while defaulted derived constructors are unaffected.
- `PAT_precede_nested_dependent_types_with_typename` now illustrates the rule with a
  declaration inside a function body rather than with a `using` alias, which C++20's
  type-only contexts made optional, and records that implementations have taken that
  relaxation up unevenly.
- `PAT_factor_parameter_independent_code_from_templates` now identifies forced
  substitution, not the `inline` keyword, as what reinstates the duplication that
  factoring removes, and cross-links the card that owns the distinction.
- `PAT_change_an_associative_element_without_breaking_its_ordering` now names which
  cast fails loudly and which one silently does nothing: `const_cast` to a value does
  not compile, while a cast that may copy modifies a temporary.
- `PAT_price_virtual_dispatch_against_the_real_alternative` no longer quotes the
  figures its own Don't clause forbids, and no longer ranks a tag-and-switch below
  virtual dispatch - measured, the switch can win at three cases. The maintenance
  objection, which holds whichever way a measurement goes, is now the stated reason
  to refuse it.

### Added

- Added `software-engineering` memory entries recording the sweep: what the probe
  method finds and cannot find, the two shapes of defect it keeps surfacing
  (benchmark numbers written into canon, and equivalences between cases that behave
  differently), and the fixture faults that precede most false alarms.

## 1.0.0-beta.6 - 2026-09-11

### Added

- Added Skillset Memory schema v2 with `specialization_profile` for tracking
  demonstrated subcategory transfer and `card_candidate` for incubating possible
  canon lessons without premature card creation. Version-1 stores remain readable
  so independently maintained domain archives can migrate when needed.
- Added an explicit card-candidate lifecycle: evidence can strengthen a hypothesis
  but never auto-promotes it; synthesis must deliberately create/refine canon,
  retain specialization-only guidance, or reject the candidate.
- Added `learned_principle` as a first-class Skillset Memory type, separating a
  durable transferable lesson from the empirical result or event that supported
  it.
- Added domain-prefixed `workspace/handoffs/` documents to project snapshot and
  import scope while keeping them outside consumer releases.
- Added new Art cartography and publication-design knowledge, Game Design
  adventure and foundation guidance, Writing fiction and adventure-module
  coverage, and corresponding domain memory evidence.
- Added commit-level Semantic Version enforcement. Repository tests require the
  working version to advance beyond `HEAD`, or a committed version to advance
  beyond its first parent, while exported trees without Git history remain
  portable.

### Changed

- Project snapshots now include canonical release recipes by default, and the
  importer carries the selected domain's matching recipe automatically.
- The Writing recipe now includes `writing/adventure-modules`.
- Limited the repository's public `workspace/` surface to reusable tools,
  canonical release recipes, and project handoffs. Existing local authoring
  material remains on disk but is no longer tracked.
- Modernized C++ guidance and its runtime profile, including corrected rules for
  top-level `const` returns, inline linkage, and class-specific allocation
  handlers.
- Made production release builds reject substantive `Unreleased` notes or a
  version missing from the public README and changelog. Release manifests now
  record that this version contract passed.

### Validation

- Validated 1,772 canonical objects, all visual references, 197 generated
  indexes, and all four Skillset Memory stores (107 entries and 241 events).
- Passed all 175 repository tests, including every canonical release build and
  check.

## 1.0.0-beta.5 - 2026-09-08

### Added

- Added bounded cross-skill auxiliary fallback groups to release recipes. The
  builder resolves card-level relationship closure, preserves canonical card and
  asset bytes, regenerates release-local indexes, and excludes foreign-domain
  Skillset Memory.
- Added deterministic authority resolution for active release manifests: one
  complete owner provider wins, identical fallbacks coalesce, and differing
  fallbacks or multiple owners fail closed.

### Changed

- Advanced `RELEASE_MANIFEST.json` to schema 2 with owned domains, complete
  packaged object IDs, and explicit auxiliary group membership and paths.
- Made release checks validate auxiliary ownership, object and file membership,
  hashes, generated routing instructions, and owned-only memory.

### Validation

- Passed all 166 repository tests, including five new auxiliary packaging and
  authority-resolution tests plus every canonical release build and check.

## 1.0.0-beta.4 - 2026-09-07

### Added

- Added one generic, model-neutral Drill administrator for every current and
  future skillset. It discovers canonical Drill cards, prepares either blind
  cut, supports same-domain Drill chains, freezes produced answers before
  revealing grading material, validates complete criterion accounting, and
  exports Skillset Memory-compatible candidate events.
- Added fail-closed lifecycle checks for premature grader material, missing or
  empty answers, symbolic-link escapes, answer mutation after freeze,
  incomplete grades, invalid-run attribution, and cross-domain chains.
- Added shared lifecycle coverage for Game Design and Software Engineering,
  including a clean extracted-release run through prepare, freeze, reveal, and
  finalize.

### Changed

- Made Drill support capability-derived during release construction. A release
  containing canonical Drill objects now vendors `scripts/skillforge_drill.py`,
  declares that fact in `RELEASE_MANIFEST.json`, and receives portable and
  manual administration instructions in its generated `SKILL.md`; releases
  without Drills carry no unnecessary runner.
- Clarified that Drill administration standardizes evidence boundaries and
  stopping behavior without selecting a model or constraining how the taker
  reasons, solves, or uses its capabilities.
- Kept release-mode training append-free: finalization creates a reviewable
  candidate event inside disposable run state and never mutates packaged,
  read-only Skillset Memory.
- Required AI-authored merge and release commits to record what changed, what
  was intentionally excluded or preserved, validation performed, and any known
  issue left behind.

### Validation

- Validated 1,625 canonical objects and all reviewed visual references.
- Passed all 161 repository tests, including all four SkillForge release builds
  and checks and 15 focused Drill-administration tests.
- Confirmed discovery of 119 Art, 14 Game Design, 71 Software Engineering, and
  89 Writing Drills without a domain registry.

### Preserved boundaries

- The runner launches no models, sub-agents, repetitions, or comparative arms;
  model execution and any batch-wide sibling cancellation remain the host
  controller's responsibility.

## 1.0.0-beta.3 - 2026-09-07

### Added

- Added 27 Game Design Patterns from the completed D&D Basic source project:
  one Adventure Pattern, nine Character Patterns, five Foundation Patterns, and
  twelve Mechanics Patterns. They cover hybrid procedural construction,
  advancement and succession, mechanically causal identity, onboarding,
  persistent rules state, pressure and resource systems, causal randomness,
  injury, time, resolution scale, and extended processes.
- Added a Software Engineering card field-test protocol for reviewing one card
  against one real human-code slice, building a proof of concept, comparing the
  engineering decisions, gating active-project use, and stopping before another
  review.
- Distinguished neutral catalog-selected corpora, project-relevant references,
  and interest-led investigations, with a blank local-context template so one
  user's source choices cannot become public defaults or control data.
- Made field-test setup model-guided: code plus a practical goal is sufficient,
  catalogs are optional, and the model maintains any local context record.
- Separated maintainer card qualification from ordinary project use, recognized
  demonstrated defects in human review subjects as useful evidence, and scoped
  single-language results instead of treating them as proof that a core card is
  language-agnostic.
- Clarified that verified language coverage does not change ownership: reusable
  decisions remain in one shared core while language modules contain only their
  language-specific realization and exceptions.
- Added a dedicated Software Engineering Drill protocol that separates
  portability probes, blind sittings, deterministic regressions, and comparative
  studies.
- Added contamination stop conditions, single-pair checkpoints, and explicit
  sub-agent concurrency and run ceilings for empirical work.
- Added a derived SE Drill inventory command and a self-testing C++ Drill packet
  that exercises compile-success and expected-compile-failure evidence.

### Changed

- Revised 26 existing Game Design objects—five Adventure Patterns, one Character
  AP, one Character Drill, five Character Patterns, five Foundation Patterns,
  one Mechanics Drill, and eight Mechanics Patterns—to integrate the new
  decisions into existing design, calibration, onboarding, progression,
  resolution, and action-economy guidance.
- Regenerated the affected Game Design indexes. The package now contains 159
  validated objects.

### Safety and evidence

- Imported the returned Game Design project through the domain-only project
  boundary. Shared documentation, tools, root instructions, runtime code, and
  Python cache artifacts present in the archive were deliberately excluded as
  stale or out of scope.
- Reviewed the imported card delta after the archive passed card, reference,
  index, and Skillset Memory validation. No repository files were deleted by the
  import.

## 1.0.0-beta.2 - 2026-09-06

### Changed

- Generalized code-corpus measurement from hardcoded C and C++ handling to
  explicit C, C++, Go, Python, and Rust language profiles.
- Excluded conventional test files, Rust inline test modules, and testing
  frameworks' own assertion macros from production-code measurements while
  retaining qualified production assertion macros.
- Retired the obsolete Art pressure harness after blind Drills replaced its
  evaluation role.

### Evidence

- Reproduced the recorded C, C++, and Rust density baselines with the current
  instrument and named the corpora behind those figures.
- Recorded a new blind agent-authored corpus measurement, including the result
  that assertion density alone could not distinguish the compared samples.

## 1.0.0-beta.1 - 2026-09-06

First formal public beta. Earlier development was not assigned public SemVer
releases.

### Added

- Portable PASS authoring, schema, validation, memory, project-snapshot, import,
  runtime, and release-building workflows.
- Python-capable chat project snapshots for Art, Game Design, Software
  Engineering, and Writing.
- Self-contained SkillForge releases for all four current domains.
- Split AGPL-3.0-or-later and CC BY-SA 4.0 licensing, contribution guidance,
  attribution, project-name protection, and community support links.
- A documented Drill model for AI training and evaluation, with future
  AI-guided human teaching identified as a separate maturity target.

### Beta compatibility notice

The intended `1.0.0` public surface is now documented. Incompatible corrections
may still occur during beta, but they must receive a new prerelease version and
release notes. Published version contents are not replaced silently.
