# Changelog

PASS follows [Semantic Versioning 2.0.0](https://semver.org/). This file records
user-visible changes to the PASS factory contract. Individual SkillForge
skillsets may evolve independently.

## Unreleased

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
