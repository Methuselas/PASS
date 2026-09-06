# Contributing to PASS

Contributions are welcome: corrections, new cards, stronger tests, runtime and
tooling improvements, documentation, and complete new skillsets can all become
part of PASS.

## Start with the owning instructions

Read `AGENTS.md`, then use the matching skill under `.agents/skills/` for the
work. PASS deliberately authors one domain per run. A contribution to one
skillset must not inspect or modify another skillset to make its change work.

For knowledge changes, follow `PASS/SKILL.md` and the phase-specific references
it routes to. Cards must remain valid and executable after their source is gone;
do not copy source passages, page references, research receipts, chat history, or
practice history into canonical cards.

## Adding a skillset

A new independent skillset normally includes:

- a package under `library/<domain>/` with valid modules and cards;
- optional empirical history under `memory/<domain>/`;
- matching repository discovery skills under `.agents/skills/` and
  `.claude/skills/`; and
- a canonical `SkillForge_*.yaml` release recipe when the skillset is ready for
  distribution.

Do not add a global registry or hand-maintained repo-wide index. Discovery comes
from the library, and generated indexes come from the cards.

## Validate the contribution

Run the relevant focused checks while working, then run the complete boundary
before proposing a repository-wide change:

```bash
python PASS/tools/validate.py
python PASS/tools/verify_references.py
python PASS/tools/build_index.py --check
python PASS/tools/memory.py validate
python -m unittest discover -s tests -p "test_*.py"
```

If the contribution changes a release boundary, build and check the affected
release as described in `README.md` and `PASS/docs/MODULE_RELEASES.md`.

## Licensing contributions

PASS uses split open licensing:

- executable tools and runtime code are AGPL-3.0-or-later;
- authored knowledge, Skill instructions, documentation, declarative profiles,
  recipes, and original assets are CC-BY-SA-4.0.

By submitting a contribution for inclusion, you agree to license it under the
terms applicable to its destination and represent that you have the right to do
so. Identify third-party material and its license explicitly. Do not submit
material copied from a source merely because PASS studied that source.

See `LICENSE.md`, `NOTICE.md`, and `TRADEMARKS.md` for the complete project
policy.
