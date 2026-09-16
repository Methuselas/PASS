# Handoff — algorithms reading order, 2026-09-15

Disposable. Not authoritative. Discard when stale.

## Done and committed

Item 3 of `D:\Sources\Programming\Algorithms\READING-ORDER.md` (Heineman,
Pollice, Selkow — *Algorithms in a Nutshell*, 2nd ed.) is **closed**. All
thirteen units have now been read: six on 2026-09-07, the remaining seven on
2026-09-15.

- `6750adb` — u02, u04, u06. Four new cards plus one refinement.
- `fc6b16b` — u08, u10, u13. Two new cards plus one refinement.

Cards landed, all in `library/software-engineering/core/`:

- `performance/PAT_read_a_break_in_the_cost_curve_as_a_change_of_strategy` (u02)
- `problem-solving/PAT_detect_a_degrading_run_and_switch_to_a_bounded_method` (u04)
- `problem-solving/PAT_keep_the_order_of_equal_keys_when_it_carries_information` (u04)
- `performance/PAT_pin_the_relationship_between_input_sizes_before_ranking_two_costs` (u06)
- `performance/PAT_measure_how_much_your_index_actually_prunes` (u10)
- `performance/PAT_report_the_spread_not_just_the_number` (u13)

Refinements: `PAT_estimate_the_order_before_you_run_it` (adaptivity, u02) and
`PAT_reduce_your_problem_to_one_that_is_already_solved` (the generality ladder,
u08). u01 was read in full and produced no card.

Per-unit dispositions and every rejection with its named owner are in
`workspace/authoring/algorithms-nutshell-remainder/RUN_NOTES.md`. That folder is
per-book scratch and should be deleted now the book is closed.

## Open, and the reason this session stopped

**The full unittest suite reports 211 tests, 14 failures.** This was discovered
after both commits landed. It is NOT yet established whether any failure belongs
to the cards above; the evidence so far points elsewhere but is incomplete.

What is known:

- The one failure name captured is
  `test_skillforge_code_study.SkillForgeCodeStudyTests.test_software_release_vendors_the_code_apprenticeship_runner`,
  which is another session's **untracked** test file exercising their untracked
  `PASS/runtime/skillforge_code_study.py`. It fails on `AssertionError: 1 != 0 :
  FAIL: quality gate failed (validate.py)`.
- `validate.py` fails at HEAD on
  `library/software-engineering/languages/cpp/algorithms/PAT_reach_for_a_named_algorithm_before_writing_the_loop.md`
  — rule 8, unreplaced angle-bracket token. The backticked C++ include on line 68
  reads to the validator as a template placeholder. That card was committed by
  another lane in `396365a` and was not touched here. Every test that shells out
  to `validate.py` will fail while it stands.
- The other 13 failure names were lost: the run was piped through `tail -15`,
  which both truncated the output and masked the exit code (the `0` observed was
  `tail`'s).

**UPDATE, later the same day.** Codex resumed and fixed the cpp card in the
working tree; it now says "the standard algorithm header" instead of the
backticked include, and `validate.py` reports PASS over 1778 objects. The fix is
uncommitted, so HEAD still fails. The 14 failures were very likely downstream of
that validate failure but this has NOT been confirmed by a re-run. Codex is live
in the package again, so do not edit there without checking first.

**Next action:** re-run `python -m unittest discover -s tests -p "test_*.py"`
with full output captured and no pipe, name all 14, and determine whether any is
attributable to this run's cards. Expect most or all to be downstream of the
cpp rule-8 failure. Fixing that card belongs to the lane that owns it.

## Also outstanding

**Neither commit advances the Semantic Version**, deliberately and with the
user's explicit approval. `VERSION`, `README.md` and `CHANGELOG.md` carry
another session's uncommitted `1.0.0-beta.25` release whose notes describe
controller code that is still untracked; bumping would have either overwritten
their work or shipped notes for code not in the commit. Note also that `396365a`
itself landed three cards with no bump. The version rule is owed for all three
commits and should be closed when beta.25 lands.

## Next in the reading order

**Item 4, CLRS (3rd ed.) — fully open.** A preflight was produced and presented
but NOT confirmed, and no CLRS text has been read. It is recorded here only so
it need not be re-derived; it is a prediction, not a finding.

- 1313pp, 35 chapters + 4 appendices, clean text layer.
- Subject: design an algorithm, argue it correct, analyse what it costs. The
  Preface addresses instructors and may not set the subject.
- Units: 39 candidates, chapter-grained, provisional. Ch34 and Ch15 are the
  likeliest to split on a read.
- Six units predicted to hold residuals, ~179pp total: **Ch2** loop invariants,
  **Ch5** randomisation against an adversary, **Ch11** universal hashing,
  **Ch14** augmenting data structures, **Ch17** amortized analysis (the only
  one predicted new-heavy), **Ch27** multithreaded work/span.
- Everything else predicted low, because Dasgupta and Nutshell already mined
  CLRS's design-technique core.
- Recommended mode: unit ingestion scoped to those six. Curriculum audit is what
  §1.4 would suggest for a mature region, but a structural read of 1313pp is not
  cheap and is the shape the reverted 2026-09-07 episode collapsed into.
- Appendices A–D, Preface, Bibliography, Index: `no-extract`.

**Warning carried forward:** everything CLRS-related from the reverted episode is
void. Any note naming a resize-hysteresis overlap, an amortized-analysis card, or
a work/span combine-step refinement is memory of a reverted attempt's reasoning,
not evidence about the current library, and must be re-derived from the text.
