# Software Engineering — Python Track Handoff

**Status:** start-of-track brief for a fresh session. Written 2026-09-13.
**Release boundary:** workspace only. Never commit this file or ship it in a release.

## Why this track exists

`library/software-engineering/core` (349 Patterns, 23 APs, 54 Drills) is meant to be
language-agnostic, but `languages/cpp` is the only language module under it, so every core
claim has only been exercised through C++. The user calls core "extremely brittle" for that
reason. Decisions already made, do not reopen:

- **The core sweep is on hold** until other language modules exist.
- **Adding language modules comes before finishing the algorithms reading spine.**
- **Python is the first new language.** It is the language most unlike C++ — garbage collection
  instead of destructors, dynamic typing, duck typing, exceptions as ordinary control flow, the
  GIL — so it is the best test of whether core's "agnostic" claims are really C++ habits.
- **Every card must be current for today's Python**, not for the edition of the book.

The C++ module is finished for this pass: patterns compile-probed and repaired, all 17 Drills and
9 Action Protocols updated. Its closing state: PASS `6bee6b3` (1.0.0-beta.19) and SkillForge
`e529ca9`, both pushed. Software-engineering memory is at `memory_version: 37`, events through
`SE_EV_0088`.

## Target Python version

- **Target the latest stable release.** On this machine that is Python 3.14.4, run as `py -3.14`.
  Before the preflight, check python.org for a newer stable release (3.15 is scheduled for about
  October 2026) and use whichever is current. Don't take this note's word for it.
- **`python` on PATH is 3.12.10.** PASS's own tools run on it; that is fine. **Probes of card
  claims must run under the target version** (`py -3.14 probe.py`). Where a card says a feature
  arrived in a version, run it on 3.12 too to confirm the boundary.
- **No free-threaded build is installed** (`py -0` lists only the standard 3.14). Any claim about
  what the GIL does or doesn't protect needs care: free-threaded CPython stopped being experimental
  around 3.13–3.14. Verify its status in the target version's "What's New", and either install the
  free-threaded build to probe it or label such a claim untested on that build.

### Currency rule

The spine books are years behind; edition years in the filenames run from 2009 to 2017, and the
rest must be read off each PDF's copyright page during preflight. So every candidate card is
checked against current Python **before it is presented**, not in a later sweep:

1. **Consult the currency authority.** The official "What's New in Python 3.x" pages, from the
   book's version up to the target, plus the relevant PEPs. Treat them as a **reference to
   consult, not a source to extract**, the same role the C++ Core Guidelines had.
2. **Run every claim.** Anything the card says Python does, prints, raises, costs or refuses gets a
   probe under the target version. The C++ sweep's strongest finding was that source age predicts
   defects, and that a "modernized" sentence can keep an old conclusion over a new mechanism.
3. **Version-gate on the card.** Where the right advice depends on a minimum version, say so in the
   body. Never write a card whose advice is stale for current Python because the book said it.

Areas where 2010s books are most likely stale; this is a checklist, not a claim. Verify each in
"What's New":

- structural pattern matching;
- typing (generics syntax, the `type` statement, annotation evaluation);
- `asyncio` (task groups, cancellation, timeouts);
- exception groups and `except*`;
- free-threading and subinterpreters;
- f-string grammar and template strings;
- `dataclasses`;
- `pathlib`;
- the removal of `distutils` and other dead batteries;
- packaging (`pyproject.toml`).

## Sources

Reading order: `D:\Sources\Programming\Python\READING-ORDER.md`. Read it whole. It is a general
learner's order, so the preflight must re-rank it for PASS, where **cards are execution, not
teaching**.

Spine as listed:

1. `Mark Lutz - Learning Python, 5th Edition - 2013.pdf`
2. `Automate The Boring Stuff With Python - Practical Programming For Total Beginners.pdf`
3. `Beyond the Basic Stuff with Python. Best Practices.pdf`
4. `Introduction to Computation and Programming Using Python.pdf` (Guttag)

Specializations the order lists: Alchin *Pro Python* (2010), *Supercharged Python*, Lutz
*Programming Python* 4th ed. (2010), Forbes *Learning Concurrency in Python* (2017), Beazley
*Python Essential Reference* 4th ed. (2009; reference, not reading), Karumanchi (algorithms),
VanderPlas and ML titles (data/ML). Also in the folder but not in the order: *Expert Python
Programming* (edition unknown). The rest of the folder is beginner filler; the order says skip it.

Expectations to test during preflight, not decisions:

- **Guttag** is CS thinking. Its material lands in `core`, not `languages/python`, and core is on
  hold. It likely triages out for this track, or yields only core-contact evidence (below).
- **Automate the Boring Stuff** is a beginner task book. Expect near-zero yield.
- **Lutz, *Learning Python***, is ~1,600 pages and 2013. The yield is probably concentrated in the
  object model, scopes and closures, iterators and generators, and decorators. Expect heavy
  currency correction.
- **Beyond the Basic Stuff, Pro Python, Supercharged Python, Expert Python Programming and Forbes**
  are likely the highest yield per page for a module whose job is to correct defaults.
- **Watch the value test.** The model already writes fluent Python. A card earns its place only
  where the common default is wrong or a trap is invisible: mutable default arguments, late-binding
  closures, `is` versus `==`, what the GIL does and doesn't protect, `asyncio` cancellation, and so
  on. Idiomatic advice the model already follows is not a card.

Extract with `pdftotext -layout` into the session scratchpad. Nothing is copied into the repo.

## Where cards go

- **New package:** `library/software-engineering/languages/python/`, with a `MODULE.yaml` shaped
  like `languages/cpp/MODULE.yaml` (`requires: software-engineering/core`). The software-engineering
  skill already says new language modules belong there, so this is not a new convention.
- **A card goes to `languages/python` only when its IF/THEN cannot be stated without a Python
  construct.** Otherwise it belongs to core.
- **Core is on hold.** Don't add or edit core cards in this track without the user's explicit
  approval.
- **A language-specific variant folds into an existing card in its own language package, never
  into a core card body.** Cross-references may name own-package cards plus `metaskills`.
- **Adding a module means updating its release recipe in the same change:**
  `workspace/release-recipes/SkillForge_Software_Engineering.yaml` (modules list, and its
  description, which currently names only C++). The runtime profile
  `PASS/runtime/profiles/software-engineering.yaml` and the repo skill wrappers under `.claude/` and
  `.agents/` also mention C++; check whether each needs Python named. Wrapper text is shared, and a
  test enforces the pairs match.

### Core contact: the reason this track exists

When a Python unit touches something a core card already owns, don't just skip it as owned. Run
the core claim in Python and record whether it held, in the unit's field note under **Core
contact**:

- **held:** the claim is true in Python as stated;
- **broke:** the claim is false in Python; name the C++ assumption it smuggled in;
- **narrower:** true only with a qualifier.

This is evidence for the later core sweep. Report breaks to the user in the sitrep, and **do not
repair core** without approval.

## Procedure

Follow `PASS/docs/PASS_RUN.md` literally, via the `pass-authoring` skill.

- **Check the git log first.** Run `git log --oneline -30` and `git log --all --oneline | grep -i
  python` so no finished work is re-done.
- **Check nobody else is working in the package.** Three agents share the repo, and the collision
  unit is the top-level package. Confirm nobody else is live in `library/software-engineering` or
  `memory/software-engineering`.
- **Preflight one source at a time.** State the subject (front matter doesn't set it), rule on each
  unit, map each to its library region with prior-card counts, and **present it and get
  confirmation before reading**.
- **Work one unit at a time.** Read it in full, then give a sitrep with named dispositions and a
  fully drafted delta. Land only on approval: one commit per closed unit, staging only that unit's
  files.
- **Do the third read before presenting:** the unit's cards, read cold against `PASS_SCHEMA.md`.
  `validate.py` is the floor, not the check.
- **Triage out freely.** Drop a source or unit with a one-line reason. The backtrack queue is
  retired.
- **Every commit** advances `VERSION` (beta suffix), the two version mentions in `README.md`, and a
  dated `CHANGELOG.md` entry. The commit body states what changed, what was excluded, which
  validation ran, and known issues, and ends with the co-author line.
- **Validation before landing:**

      python PASS/tools/validate.py --package software-engineering
      python PASS/tools/verify_references.py
      python PASS/tools/build_index.py
      python PASS/tools/memory.py validate
      python -m unittest discover -s tests -p "test_*.py"   # ~6.5 min; run in background

- **Write memory events** with `python PASS/tools/memory.py append --domain software-engineering
  --json <file>`. Double apostrophes inside single-quoted YAML.
- **Commit only when the user says, and push only when asked.** The user is not a programmer; make
  the technical call and state it rather than surveying options.

## Terminology and traps

- **AP means Action Protocol.** Never "Action Pattern", "action plan" or "action procedure".
- **Cards carry no source id, page number or locator.** `reference` may name title and author only.
- **`workspace/` is never committed**, except release recipes.
- **Do not run a card claim without reading the card's whole body.** Every misreported card defect
  so far came from a card read by summary.
- **Probing:** write probe files with the file-writing tool; shell heredocs break on quoting. Keep
  the card's claims and your own expectations in separately named files, or a quirk reads as a
  card defect. When a probe fails, suspect the probe first: every early "defect" in the C++ sweep
  was a fixture answering an adjacent question.

## Later, not now

- **Found-code field tests.** `workspace/sources/Python/pydantic/` is already extracted
  (gitignored) for testing the module against real code, per `PASS/docs/SOFTWARE_CARD_FIELD_TESTS.md`.
  Do it once the module has cards, not before.
- **Drills and the SkillForge rebuild** come after the module has substance; the user decides when.

## First step for the new session

Read this file, `PASS/SKILL.md`, and `D:\Sources\Programming\Python\READING-ORDER.md`. Confirm the
current stable Python version. Then propose which source to preflight first, with the reason, and
wait for the user's choice.
