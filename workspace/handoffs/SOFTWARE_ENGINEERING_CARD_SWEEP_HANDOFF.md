# Software Engineering — Card Sweep Handoff

**Status:** Project-workspace continuation control for the compile-probe sweep of the
`software-engineering` library.
**Release boundary:** **Never ship this file with a SkillForge release.** It is project
workspace only. The field-test notes it refers to are untracked and also never ship.

## Purpose

A topic-by-topic sweep is testing every card in `library/software-engineering` against a real
compiler, repairing the ones whose claims do not survive. This document is what a fresh session
needs to continue it without re-deriving the method, the state, or the traps.

Read this, then read `PASS/docs/SOFTWARE_CARD_FIELD_TESTS.md` (the governing protocol) and the
`consumer_instructions` in `PASS/runtime/profiles/software-engineering.yaml`. Do not read the
master indexes or unrelated domain cards.

## Where things stand

Committed and pushed through **`44f59ad`, PASS 1.0.0-beta.12** (batches 16 to 20, sixteen cards).
Forty-two cards repaired in all. **Nothing is uncommitted**: the working tree holds only this
handoff, which stays untracked.

The pattern sweep is closed. **Drill currency update in progress** (agreed with the user
2026-09-13): update each C++ Drill against its linked pattern first, compiling every claim the
updated text makes; blind sittings, if wanted, come later and may be run by the user's local
model — never hand it the reference probes or field notes.

**Drill batch 1 landed as PASS 1.0.0-beta.13** (copy and resources, 5 Drills), approved by the
user, together with the fourth ownership option (neither copyable nor movable) in
`PAT_choose_raii_copying_behavior_deliberately` and `AP_write_copy_control_for_a_resource_owning_class`.
Field note `workspace/field-tests/2026-09-13_cpp_drills_copy_and_resources_update_batch.md`;
memory event `SE_EV_0081`, no memory entries changed (`memory_version` still 36). Not pushed.

**Drill batch 2 landed as PASS 1.0.0-beta.15** (class surgery: pimpl conversion, pimpl swap,
const-correctness, initialization list), approved by the user, together with the non-propagating
`const` warning added to `PAT_minimize_compilation_dependencies` and the pimpl Drill. Field note
`workspace/field-tests/2026-09-13_cpp_drills_class_surgery_update_batch.md`; memory event
`SE_EV_0082`. PASS 1.0.0-beta.14 (`1168a58`) pins UTF-8 on the release builder's and tests'
subprocess output. None of beta.13 to beta.15 is pushed.

Batch 2 lesson: before rewriting a whole card with the file-writing tool, read its front matter;
a card read from the heading down had its `target_skill` and tag order silently rewritten, which
the validator does not catch.

**Drill batch 3 landed as PASS 1.0.0-beta.16** (allocation and templates: conforming operator
new, placement pair, templatized base, traits dispatch), approved by the user, together with the
same-named-function warning added to `PAT_access_templatized_base_members_explicitly` and its
Drill. Field note `workspace/field-tests/2026-09-13_cpp_drills_allocation_templates_update_batch.md`;
memory event `SE_EV_0083`. The test fixture derived from the templatized-base Drill was
deliberately left unchanged. None of beta.13 to beta.16 is pushed.

**Drill batch 4 landed as PASS 1.0.0-beta.17** (mostly design: interface misuse, is-a to
composition, NVI, lock-every-member), approved by the user, with a repair to
`PAT_lock_at_the_public_boundary_and_nowhere_inside` (nested ordinary-mutex acquisition threw
`std::system_error` in every MSVC build mode rather than deadlocking) and the `std::chrono`
calendar-type note added to `PAT_make_interfaces_hard_to_misuse` and its Drill. Field note
`workspace/field-tests/2026-09-13_cpp_drills_design_update_batch.md`; memory event `SE_EV_0084`.
**All 17 C++ Drills are now updated.** None of beta.13 to beta.17 is pushed.

**Uncommitted in the working tree, held on purpose.** The user asked to finish all three AP
batches, then land every AP repair in one commit and afterwards update the SE skill and project.
- AP batch 1, ownership and copying: copy-control, resource-management, exception-safety,
  memory-management. Field note `workspace/field-tests/2026-09-13_cpp_aps_ownership_update_batch.md`.
- AP batch 2, types and interfaces: const-correctness, inheritance, virtual-functions. Field note
  `workspace/field-tests/2026-09-13_cpp_aps_types_interfaces_update_batch.md`.
- AP batch 3, containers and concurrency: containers, concurrency. Field note
  `workspace/field-tests/2026-09-13_cpp_aps_containers_concurrency_update_batch.md`.
All nine C++ APs updated and **landed as PASS 1.0.0-beta.18 (`d62d09a`, message reworded from
`4ed7948`)** with memory events `SE_EV_0085`–`SE_EV_0087`. Then **beta.19 (`6bee6b3`)**: APs named
Action Protocols everywhere, and the erase card led with C++20 `std::erase`/`std::erase_if`
(`SE_EV_0088`, `memory_version` 37). SkillForge Software Engineering rebuilt from `6bee6b3`
(1,965,536 bytes, SHA-256 `e29d6e53…46ed`) and committed in SkillForge; the software-engineering
project snapshot rebuilt with tests and recipes and dry-run imported with 0 changes. Neither
repository is pushed.

**The C++ module is finished for this pass. Stop here:** core waits for other language modules.

Next: the 9 C++ Action Protocols, **then stop.** The user decided on 2026-09-13 not to sweep the
core package yet: with `cpp` the only language module, core's agnostic claims are brittle, so other
language modules come first — ahead of core and ahead of finishing the algorithms reading spine.

Original batch plan, for reference: allocation and templates (conforming operator new, placement pair,
templatized base names, traits dispatch), mostly design (interface misuse, is-a to composition,
NVI, class that locks every member).

Batch 1 lessons for the next batches: a Drill can carry a defect its swept patterns do not, so
probe every quantity and every "or default"-style permission; strip book item numbers from Notes;
move answers out of Instructions into the Success Check; and grep the package for any list a
change extends (the ownership options also lived in an AP). `<Type>` in backticks trips the
validator's angle-bracket rule — write "`std::unique_ptr` member owning the `Bitmap`".

Every batch left a note in `workspace/field-tests/` (untracked, and deliberately so — they are
evidence, not canon). Twenty-three exist: twenty batch notes plus three single-card field tests from
the start of the sweep, before the batching method existed. The last is
`2026-09-12_cpp_algorithms_compile_probe_batch.md`. Read the note for a topic before re-testing it —
it records what was measured, what the numbers were, and what was deliberately left untested.

Memory state: `memory_version: 36`, 26 entries (`SE_MEM_001`–`SE_MEM_026`), 80 events ending at
`SE_EV_0080`. The sweep's own events are `SE_EV_0058`–`SE_EV_0080`.

**Driver trap found in batch 15:** never call `find` from a `.bat` launched through Git Bash. It
resolves to the POSIX tool and walks the whole drive. Use `findstr`.

**Batches 12 and 13 broke the taxonomy below.** Five of their eight defects were language-rule
claims, all from Meyers' pre-C++11 books (*Effective C++*, *More Effective C++*), while the
*Effective Modern C++* cards held every rule. Read the updated `SE_MEM_025` before aiming the next
batch: source age now predicts language-rule defects better than claim kind does.

### C++ patterns tested (176 of the module's 176)

    concurrency           21   2 repaired
    resource-management    6   1 repaired
    move-semantics         3   1 repaired
    templates             13   2 repaired
    containers            15   1 repaired
    virtual-functions      8   1 repaired
    copy-control           8   clean
    inheritance            7   1 repaired
    exception-safety       4   clean
    undefined-behavior     2   2 repaired
    traits                 2   clean
    preprocessor           2   1 repaired
    optimization           2   clean
    destructors            2   clean
    swap                   1   clean
    metaprogramming        1   clean
    language-interop       1   1 repaired
    variable-definitions   1   clean
    compilation-dependencies 1 clean
    inlining               1   clean (field-tested individually, batch 2)
    casting                3   clean (batch 12)
    construction           3   2 repaired (batch 12)
    interface-design       3   1 repaired (batch 13)  design_a_class_as_type untested
    encapsulation          3   clean (batch 13; mostly design, mechanical claims only)
    type-deduction         3   clean (batch 13)
    lambdas                3   1 repaired (batch 14)
    coroutines             3   2 repaired (batch 14)
    iterators              4   1 repaired (batch 15)
    initialization         4   3 repaired (batch 15)
    const-correctness      5 of 5 cards (batch 16 took the other 4)  2 repaired in all
    parameter-passing      5   3 repaired (batch 16)
    operators              8   4 repaired (batch 17)
    foundations            8   2 repaired (batch 18)  adapt_rules_to_active_cpp_sublanguage untested
    memory-management     10 of 10 (batch 19 took the other 9)   4 repaired in all
    algorithms            10   3 repaired (batch 20)  reach_for_a_named_algorithm mostly untested

Every C++ pattern topic is done.

### Not yet swept

    C++ patterns:          none                                         0 patterns
    core package:          349 patterns, 23 APs, 54 Drills              untouched
    cpp APs and Drills:    9 APs, 17 Drills                             untouched

176 + 0 = the module's 176 patterns, so that inventory is complete: nothing in the C++
module is missing from one of the three lists above.

The user's stated order was patterns first, then Drills, then Action Protocols.

## The method

One topic per batch. For each card:

1. **Read the whole body**, not the Pattern Rule. Reporting a card defective without reading its
   body has produced false reports before; the missing piece is usually in the Do or Notes.
2. **Compile what it prescribes** — a probe program with one `Check(claim, condition)` line per
   claim, printing `ok`/`FAIL` and a failure count as its exit code.
3. **Compile what it says must fail** — one `x*.cpp` per claim, each expected to be rejected. The
   driver reports `rejected as claimed` or `COMPILED - THE CLAIM IS WRONG`.
4. **Run what it claims about behaviour** — counters for which operation ran, which path was
   taken, what state survived.
5. **Measure what it quantifies** — timing, `sizeof`, allocation counts through a replaced
   `operator new`, object-file size, or an assembly listing.
6. **Repair only what the evidence contradicts.** Every repair so far corrected mechanics, an
   example, or a stated reason. No card's rule or direction has needed changing.
7. Write the field note, append the memory event, update memory entries, validate, run the suite,
   report, stop.

### Where the artifacts go

- Probes: the session scratchpad. Nothing in the repo.
- Field note per batch: `workspace/field-tests/<date>_<topic>_compile_probe_batch.md` (untracked).
- One event per batch: `python PASS/tools/memory.py append --domain software-engineering --json <file>`
  (write the JSON to a file first; inline heredocs break on quoting).
- Memory entries: hand-edited in `memory/software-engineering/skill_memory.yaml`, incrementing
  `memory_version`. Escape apostrophes inside single-quoted YAML scalars by doubling them, or
  `memory.py validate` fails.

### Validation, every batch

    python PASS/tools/validate.py
    python PASS/tools/verify_references.py
    python PASS/tools/build_index.py
    python PASS/tools/memory.py validate
    python -m unittest discover -s tests -p "test_*.py"     # ~6.5 minutes, run in background

## Toolchain

MSVC 19.50, VS 18 BuildTools. There is no compiler on `PATH`; everything goes through a batch
file that sources vcvars first:

    call "C:\Program Files (x86)\Microsoft Visual Studio\18\BuildTools\VC\Auxiliary\Build\vcvars64.bat" >nul 2>&1
    cl /nologo /EHsc /W4 /std:c++20 /permissive- /O2 /MT <file> /Fe:obj\x.exe /Fo:obj\x.obj

Notes that cost time to rediscover:

- `cl` must be invoked from a `.bat`; a `cmd //c "... && cl ..."` chain silently does nothing.
- `/Fa<name>.asm` for a listing — `/Fa:<name>` is parsed as a filename starting with a colon.
- Multiple source files with `/Fo:` need a directory, not a file name.
- `/std:c++23preview` for C++23 checks. `/Wall` for the "does anything warn" questions.
- `/fsanitize=undefined` does not exist here; only `/fsanitize=address`.
- Writing probe files: use the file-writing tool. Shell heredocs have broken repeatedly on
  quoting, and `\n` inside a Python-written C++ string literal turns into a real newline unless
  escaped as `chr(92) + 'n'`.
- Timing: best-of-N, and for a mechanism comparison hold the data access equal or the measurement
  reports memory layout instead.

## What the sweep has learned — read this before probing

Recorded as `SE_MEM_019` through `SE_MEM_026`; query with
`python PASS/tools/memory.py query --domain software-engineering --cues "..."`.

**The defect taxonomy.** Across eleven batches, claims about **what the language requires** have
held without exception. Every defect has been one of:

- a claim about **what a compiler reports or emits** — stated as an outcome rather than an
  entitlement (a fold that did not happen, a null test not removed, an error message that named
  something else, a warning that does or does not appear);
- a claim about **what a platform measures** — a ratio carried from another machine that inverted
  here;
- a claim that **two cases behave alike**, or that two cases are ruled out together when one of
  them is fine;
- a claim that **a tool is available** that this toolchain does not have.

So aim first at cards carrying numbers, comparisons, predictions about diagnostics, or the phrases
"the same way", "likewise", "and neither will". Cards stating language rules have been reliable.

**The probe is the likeliest thing wrong when a check fails.** Every false alarm so far was the
fixture answering a question *adjacent* to the claim. The specific traps:

- a type trait answers what compiles, not what runs (`is_move_assignable` is true for a class with
  no move assignment, because assignment from an rvalue resolves to the copy);
- the `noexcept` operator asks about a whole expression including argument conversions, so
  `noexcept(f("literal"))` is false for a `noexcept` f;
- a non-dependent `requires`-expression is ill-formed rather than false — route "does this compile"
  questions through a named concept;
- threads that never overlapped (use a `std::latch`, not a flag);
- a predicate `wait_for` returns true when the timeout fires and the predicate is then satisfied,
  so stranding looks like success — measure the wait;
- `out.str().begin()` and `out.str().end()` are iterators into two different temporaries;
- a demonstration whose inputs take the branch that hides the effect (the macro double-evaluation
  needed the argument to *win* the comparison);
- a comparison that measures parameter passing instead of the abstraction.

Diagnose a failure before reporting it. Correcting such a fixture is also how two real defects
surfaced, so a fixture fault is not merely noise.

## Limits this method cannot reach

- **Ordering claims are not falsifiable on x86-64.** The three memory-order cards are confirmed on
  their mechanical claims only. That family needs a sanitizer, a model checker, or an ARM64 target.
- **No undefined-behaviour sanitizer on MSVC**, so cards recommending one cannot be exercised here.
- **Design-judgment cards cannot be probed** — whether a parameter split is orthogonal, whether a
  boundary is the right one, whether variation belongs at compile time. Roughly five cards so far
  were counted as *untested* rather than passing. They need review against real code, which is the
  other route in `SOFTWARE_CARD_FIELD_TESTS.md`.

## Committing

Only when the user asks. Then, in the same commit:

- `VERSION` advanced (increment the beta suffix);
- the two version mentions in `README.md`;
- a dated `CHANGELOG.md` entry under `## Unreleased`, one bullet per repaired card saying what
  changed and why;
- a commit body stating what changed, what was preserved or excluded, which validation ran, and
  what is left broken or untested;
- `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`.

The test suite enforces the version advance. Commits go directly to `main`, which is this
repository's convention.

## Coordination

Three agents share this repository and the collision unit is the top-level package, not the
directory. This sweep holds `library/software-engineering/**` and `memory/software-engineering/**`.
The user's third agent (a local Qwen) was not ready as of this handoff; if it is given work in
those paths, land or checkpoint any uncommitted batch first.

## Suggested next step

Every C++ pattern is swept, landed and pushed. Next, per the user's stated order: the C++ Drills
(17), then the C++ Action Protocols (9), then the core package. **The Drills batch is pending a
conversation with the user about how to approach it** — a Drill is not a claim list, so the
compile-probe method above may not transfer as-is. Settle the approach with the user before
probing.

Batch 20 added a harness rule: a debug-CRT probe that may assert must redirect CRT reports to
stderr first (`_CrtSetReportMode` / `_CrtSetReportFile`), or the assertion dialog blocks the driver
until it times out.

Batch 18 revised the targeting heuristic: its only defects were in *Effective Modern C++* cards,
which had held for four batches. Distance from C++20 is the signal, and a C++14 source stands at a
distance; only C++20-era cards have held without exception. Before repairing any card, grep the
package for the same stale claim, because three corrections so far reached one card and missed
another saying the same thing.

Batch 17 added one more method note: when a card states a language rule correctly, still run it.
The operators batch found MSVC evaluating free overloads of `&&` and `||` right operand first,
against a sequencing rule the card had right, and confirmed it with a minimal program at three
settings before attributing it to the compiler.

Batch 16 added two method notes. Put timed callees in a separate translation unit, because
`__declspec(noinline)` does not stop the optimizer folding a callee's result into the caller and
the reference forms timed at 0.00 ns. And when a card says an already-modernized rule, check that
its example still demonstrates it: two modernized cards kept an old conclusion over a new mechanism.

Two traps from batch 15 worth carrying: memory YAML observations are single-quoted, so every
apostrophe in added prose must be doubled (it failed twice in one paragraph); and a card whose Notes
say "this caveat no longer holds" should have its Do, Don't and Checklist grepped for the caveat,
since the correction may never have reached them. Given batches 12–14, aim first at
cards whose `reference.source_title` stands furthest from C++20, whether older (*Effective C++*,
*More Effective C++*) or pre-standard (anything written against a TS). Probe their rules, not only
their illustrations.

Batch 14 added one more habit: build every lifetime program twice, under ASan and plain. The plain
build shows what a user actually sees, which is often the correct value read from freed memory,
and that is what the cards mean by "appears to work".

Batch 13 also found a card repeating advice a newer card in the same package had already corrected
(const return values). The topic-by-topic sweep does not look across topics for that, so when a
card states a rule, grep the package for a card owning the opposite rule.

ASan is available and works out of process (`/O1 /Zi /MT /fsanitize=address`); batch 13 used it to
turn two dangling-handle claims from "undefined" into an observed heap-use-after-free, each with a
kept-alive control. Use it wherever a card says something dangles.

Three things batch 12 taught about method:

- **Try every other route, not only the one the card names.** The allocation-function defect only
  surfaced because the probe tried `::new`, `new[]`, `make_shared` and a container after the
  card's own `new R` was correctly refused. A restriction card that passes its own example has
  not yet been tested.
- **Label expect-fail files by who made the claim.** One file was filed as a card claim when it
  was the reviewer's own reading of the standard, and it "failed". Keep the card's claims and
  your own expectations in separately named files, or a compiler quirk reads as a card defect.
- **No second compiler is installed.** Where a result looks like a compiler gap rather than a
  language rule, word the repair as one implementation's measurement, as batch 12 did for the
  defaulted private constructor.
