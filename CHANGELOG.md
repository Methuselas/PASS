# Changelog

PASS follows [Semantic Versioning 2.0.0](https://semver.org/). This file records
user-visible changes to the PASS factory contract. Individual SkillForge
skillsets may evolve independently.

## Unreleased

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
