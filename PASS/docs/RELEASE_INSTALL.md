# Using a SkillForge Release

A finished release is one self-contained Agent Skills-compatible directory. It has
`SKILL.md`, `RELEASE_MANIFEST.json`, and a local `library/` containing the complete
metaskill + prerequisite closure. It also carries `LICENSE.md`, `NOTICE.md`,
`TRADEMARKS.md`, `CONTRIBUTING.md`, and the complete applicable license texts
under `LICENSES/`, so its rights and attribution survive independently of the
PASS and SkillForge repositories.

## ChatGPT / Codex skills

Where standalone Agent Skills are supported, install or upload the release
directory/ZIP as a skill. The root `SKILL.md` carries the required `name` and
`description` metadata.

For repository-local Codex discovery, place a released skill directory beneath:

```text
.agents/skills/<skill-name>/
```

PASS keeps repo-only discovery wrappers under `.agents/skills/`; those
wrappers are factory integration and are not copied into released skillsets.

Keep the release root intact when installing or redistributing it. Its licensing
and attribution files apply to the bundled software and knowledge and are part of
the checked package, not optional surrounding documentation.

## Claude Code

For project-local Claude Code discovery, place the release directory beneath:

```text
.claude/skills/<skill-name>/
```

PASS keeps matching repo-only discovery wrappers under `.claude/skills/` for
working on the factory itself. They are not runtime dependencies of releases.

## Archive/context use

A release remains a normal self-contained directory/ZIP even when a host does not
install it as a native skill. The consumer may inspect `SKILL.md` and the bundled
`library/` directly. No PASS repository path is required.

## Execution contract and deployment profiles

Portable releases vendor the canonical SkillForge resolver as
`scripts/skillforge_runtime.py` and a declarative `runtime/profile.yaml`.

`runtime/profile.yaml` is the release's **execution contract**: it declares the
execution modes, routing, risk checks, and completion requirements the consuming
skill is expected to honor. The vendored script is an optional deterministic
helper that resolves a request against that contract and can audit a completion
record afterward. It does not run by itself, hold state, or gate anything — a
host that never invokes it still has a complete, usable release. Honoring the
contract is the consuming skill's responsibility. See `EXECUTION_CONTRACT.md`.

The generated `SKILL.md` is a router, not a copy of the complete profile. Do not
preload the profile or its generated `references/execution-barriers.md` for pure
discussion, critique, help, or another non-productive request. Before productive
work, load the barriers and prefer the resolver's bounded result; read the full
profile directly when the resolver is unavailable or when inspecting the runtime
contract itself.

Releases that carry auxiliary fallbacks include an additional router section.
When several SkillForge skills are active for one task, compare their manifests
before loading the fallback cards:

```text
python scripts/skillforge_runtime.py authority \
  --manifest <first-release>/RELEASE_MANIFEST.json \
  --manifest <second-release>/RELEASE_MANIFEST.json
```

The command selects one complete owner provider when available, otherwise the
requesting release's fallback. It refuses multiple owners and differing active
fallback payloads. Running `authority` without `--manifest` inside an extracted
release checks that release alone. A host without Python follows the same rules
from `RELEASE_MANIFEST.json`; no network service is required.

If the release contains canonical Drill cards, it also vendors the optional
model-neutral `scripts/skillforge_drill.py` administrator. It discovers only the
release-local `library/`, prepares either canonical blind cut, freezes the taker
artifact before revealing the rubric, checks that every Success Check criterion
was graded, and exports a candidate training event. It does not select a model,
dictate its reasoning, launch repeat attempts, judge craft semantics, or write
the release's read-only Skillset Memory. The generated `SKILL.md` contains the
portable/manual protocol.

A release recipe may also name a target-specific `deployment_profile`. Package
size is then measured at release build/check time against that profile. No recipe
currently names one and `PASS/runtime/deployment_profiles/` does not yet exist;
it is an available extension point. This does not change canonical authoring
validation or library organization.
