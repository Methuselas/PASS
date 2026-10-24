---
name: visual-art
description: >-
  Use for drawing, illustration, visual composition, figure or animal drawing,
  gesture, construction, anatomy, heads, hands, perspective, rendering, art
  critique, and guided visual-art teaching in this repository.
---

# Visual Art

## User help command

Treat `Help Art` and clear variants such as `Help Art staged`, `Help Art modes`, `Help Art revisions`, `Help Art references`, or `Help Art approval` as non-productive help commands. Do not generate/edit an image, change mode, ratify/reject an artifact, advance/rollback the staged workflow, or otherwise mutate production state merely because help was requested. Read `docs/ART_HELP.md` and answer from that user-facing contract. If the user separately issues a production or mode command in the same turn, follow the explicit command after answering the requested help where practical.

Use the trained Art library as canonical knowledge. Books are study material;
the accepted PASS cards and teacher corrections are the working curriculum. The
cards stand on their own — never reach for a source book to apply one.

## Targeted retrieval

Do not preload the Art master index, every subject, or every drawing system.
Classify the operation and subject, use `metaskills` as the default skill
baseline, then retrieve a bounded set from both packages with a few task cues.
Load only the relevant metaskill cards. Resolve the closest applicable AP
first, then load only the Patterns its flow reaches, plus declared foundations
and prerequisites.

```bash
python PASS/tools/find_relevant.py --package metaskills --cues "<task cues>" --limit 5
python PASS/tools/find_relevant.py --package art --cues "<task cues>" --limit 8
```

Execute a chosen AP through the runner, not from the card:
`python library/metaskills/runtime/ap_runner.py start --ap <AP_id> --task "<task>"`
(rules in `library/metaskills/runtime/README.md`). It shows one step plus the
Patterns that step names; account for each step with `done`, `gate`, or `skip`
before the next unlocks, and record produced images with `--artifact`. A runner
gate never replaces the user's approval gate in Staged Production.

For a Drill, read the applicable administration mode in
`PASS/docs/PASS_CONSUMPTION.md`; do not confuse describing an artifact with
producing it. Use the PASS-authoring skill when studying a source or changing
cards, modules, schema, or releases.

Classify the turn from meaning: discuss, inspect, or produce. Do not generate or
edit an image unless the user actually asks for production. During PASS training,
work one source chapter at a time, discuss after the read, and ask questions only
when genuine uncertainty remains.

## Skillset Memory

`memory/art/` holds this skill's current learned self-knowledge about doing its
own work: **claims** distilled from use, each a proposition that changes what
the next relevant task does. It is not the event record — that is
`training_history.jsonl` — and it is not canon, so it never overrides a card.

Canon is selected first; a Memory retrieval comes after it, is bounded, and
never selects or reroutes Canon. Retrieve with short cues drawn from the subject
and the operation:

```bash
python PASS/tools/memory.py query --domain art --cues "hand,contact,foreshortening"
```

Cues match as substrings of a claim's `retrieval_cues` and its `claim` text, so
prefer several short terms over one long phrase. A match is not an instruction:
read the claim's `delta` as what to do differently, and its `envelope` as where
that has and has not been shown to hold. A `conduct` claim may change how the
drawing is carried out; a `reach` claim may change posture, verification, or
willingness to claim a capability, and may not choose an AP. A recorded weak
area is a reason to inspect that region of the artifact more carefully after
rendering; it is never a reason to skip a risk check the routing contract
already requires.

Never copy a claim's content into a card, an index, or this file. A claim that
seems to apply on every turn has earned promotion review, not a paste.

## Conditional production contract

For any request that may generate or edit an image, read
`references/production-routing.md` before the first productive call and retain
its mode, approval, continuity, risk-inspection, and completion gates for the
active production thread. Do not load that reference for discussion, critique,
source authoring, or a Drill that produces no image.
