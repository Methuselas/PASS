# Skillset Memory

Empirical state: what actually happened when the canon was used.

```text
memory/
    art/
        skill_memory.yaml        compact current state, the file a runtime loads
        training_history.jsonl   the events it was consolidated from
```

One directory per domain, named for its `library/` package. Domains stay
independent here exactly as they do in the library — there is no shared or
global memory, and adding a domain does not touch its siblings.

The contract is **`PASS/docs/MEMORY_SCHEMA.md`**. Read it before adding
anything. The short version:

- **Memory is not canon.** It never mutates a card and is never copied into one.
  An observation that seems to apply on every turn has earned promotion review,
  not a paste.
- **An invalid run is never evidence about a capability.** A run that failed
  before the capability was exercised stays in history with a reason, attributed
  to the tool, controller, or package that actually failed.
- **Presence is not consultation.** Nothing here guarantees an entry is read.
  `memory.py query` prints what it returned so a run can record what was
  actually consulted; absent that, consultation is unproven.
- **Retrieval is bounded, and it never selects Canon.** A query ranks by match
  specificity - exact scope, then exact `canon` id, then cue and claim
  substrings - with `confidence` last and never written. The `--canon` ids are
  ones Canon selection has already pinned: Memory matches them and never
  proposes, ranks or discovers a card. A contradicted claim always comes back
  with its counterpart, which is not charged against the limit; a contradiction
  is a pair, so `contradicts` carries exactly one claim id and co-return is one
  hop that never walks a chain. An empty scope with no cues and no canon ids is
  answered as nothing rather than as a store dump.
- **A write is not persisted until the target is reopened and confirmed.**
  Every write reads back and fails loudly if the state is not there.
- **Temporary state is not memory.** Workflow position, reading progress,
  candidate status, recent artifacts, ambient context: none of it belongs here.
  The generalized lesson such state reveals may.

## Tool

```bash
python PASS/tools/memory.py validate                          # shape, vocabularies, admissibility
python PASS/tools/memory.py query --domain <domain> --scope <topic> --cues a,b --canon <card id>   # bounded retrieval
python PASS/tools/memory.py append --domain art --task "..."  # one event, verified by readback
python PASS/tools/memory.py link-evidence --domain art --claim <claim id> --events E1,E2   # one to three events behind a claim
python PASS/tools/memory.py review --domain art               # read-only: what needs a human
python PASS/tools/memory.py add --domain <domain> --json claim.json              # new claim, generated id
python PASS/tools/memory.py update --domain <domain> --id <claim id> --json '{"confidence": "strong"}'
python PASS/tools/memory.py retire --domain <domain> --id <claim id> --reason "..."
python PASS/tools/memory.py show --domain <domain> --id <claim id>
```

Change `skill_memory.yaml` through `add`, `update` and `retire`, not by editing
it. Every write validates the whole resulting store first, refuses with nothing
changed when the result would be invalid (including a claim citing an invalid
run), replaces the file atomically under a per-domain lock in `memory/.locks/`,
raises `memory_version` by exactly one, keeps untouched claims byte for byte,
and confirms the result on readback. Hand-editing is recovery only; run
`validate` afterwards.

Three write rules are worth stating here because each reverses what this file
used to say:

- **`add` generates the claim's id; a caller never supplies one.** There is no
  counter, no high-water mark, and no retired-id list to continue from. A
  retired id is never reissued, and no state exists from which it could be.
- **Currentness is presence, so retirement is removal.** `retire` deletes the
  claim and requires `--reason`. The reason is operator-facing at the moment of
  the write and is written nowhere — no tombstone, no lineage field, no
  sidecar, no History event. Evidence is untouched by this: it lives in
  `training_history.jsonl` and always did.
- **A replacement is `retire` then `add`.** There is no `supersede`. The new
  claim gets a fresh id and its own independently re-derived `confidence`;
  nothing is inherited, because no tool may compute, suggest, copy, or promote a
  confidence value.

Every command requires `memory_schema_version: 3`. A store declaring the retired
1 or 2 is refused as **unmigrated, not corrupt** - the bytes may be perfect, and
the fix is a migration rather than a repair. Nothing upgrades a store in place,
and there is no reader left for the old shape: the transition scaffolds were
deleted once the last domain migrated. An absent store stays different from a
wrong-version one: absence is silent and fails open, while a store that is there
but unreadable is always loud.

The tool is mechanical. It checks shape, retrieves a bounded set, appends an
event, links one to three representative events behind a claim, and reports what
looks stale. It never judges whether an artifact was good and never writes an
observation for you: consolidating several events into one honest sentence is a
judgment, and a script that guessed at it would be inventing empirical claims.

## Releases

`build_release.py` copies the store of every domain a release bundles to
`memory/<domain>/` in the release root, beside `library/` rather than inside
it, and writes those files read-only. A release reads the record it inherited;
it is not the target new events are written to. See
`PASS/docs/MODULE_RELEASES.md`.

## Deleting this directory

Nothing breaks. `library/` validates with `memory/` absent, and a test enforces
that. Memory is the record of using the canon, not a dependency of it.

## Seeding

An empty valid store beats a populated contaminated one. There is no requirement
to fill this in. The Art store is seeded with three craft observations from
pre-Memory practical runs; controller, tool, and packaging failures from the same
period are deliberately absent, because those were never tests of craft.
