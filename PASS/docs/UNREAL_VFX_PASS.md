# Unreal VFX PASS

Unreal VFX PASS is the asset-analysis lane for studying **existing Niagara effects**. It is intentionally separate from ordinary source authoring: `PASS/pass.py` studies a book/video/document; `PASS/vfx.py` studies a VFX asset plus temporal visual evidence.

This is a skeleton contract. The Unreal automation/plugin will eventually own live asset inspection, emitter isolation, recording, and autonomous rebuilds. The PASS side already owns the durable shape so those capabilities can be refined without changing what a completed run means.

## What the run produces

A run turns one Niagara System into evidence and candidate knowledge in this order:

1. **Inventory** — system, emitters/components, renderer types, simulation targets, timing, parameters/events when the Unreal exporter can provide them.
2. **Isolation plan** — the whole system plus every enabled emitter/component soloed without changing its own settings.
3. **Temporal capture** — still sequences for the whole system and each isolated target.
4. **Classification** — visual family/role and implementation are recorded separately. A thing may be visually a `trail` while technically using sprites rather than a Ribbon Renderer.
5. **Extraction** — reusable behavior becomes a Pattern/Recipe, repeatable qualification can become a Drill, and coordinated multi-part behavior becomes an AP/Composite Recipe.
6. **Visual validation** — candidate cards are checked against captures with observable success conditions and named near-misses before the run is complete.

The controller never writes directly into `library/`. It stages candidate cards in the run so ordinary repository review/validation remains the integration gate.

## Recipe library mapping

Niagara recipes live under:

`library/software-engineering/unreal-engine/vfx/niagara/recipes/`

- **Recipe = Pattern (`PAT_...`)**
- **Composite Recipe = Action Protocol (`AP_...`)**
- **Practice/qualification = Drill (`DRILL_...`)**

Recipes are grouped by effect family, not by one global number. Family-local variant numbering is carried in tags such as `variant_01`. Visual style is carried in `style_realistic`, `style_stylized`, `style_hybrid`, or `style_agnostic` tags so generated indexes expose it without extending the closed PASS frontmatter schema.

A finished recipe is self-contained. It may use Unreal/engine facilities named in its instructions, but it must not require another recipe, a book, a video, a page, a URL, or a source artifact to execute. Composite recipes repeat the constituent procedure they need rather than linking to child recipes as runtime dependencies.

## Capture contract

The Unreal side should eventually export an inventory JSON such as:

```json
{
  "schema_version": 1,
  "engine_version": "5.3.2",
  "project_name": "ExampleProject",
  "system_asset": "/Game/VFX/NS_BossSpawn",
  "duration_seconds": 6.0,
  "emitters": [
    {
      "target_id": "smoke",
      "name": "Smoke",
      "enabled": true,
      "renderer_types": ["sprite"],
      "simulation_target": "GPU",
      "notes": ""
    }
  ]
}
```

Start the run:

```bash
python PASS/vfx.py start --inventory inventory.json --task boss-spawn
```

The generated `capture-plan.json` requires a whole-system recording plus one isolated recording for every enabled emitter. Future UE automation can satisfy that directly. Today, recordings can be supplied manually.

A recording manifest for `workspace/tools/extract_vfx_stills.py` looks like:

```json
{
  "schema_version": 1,
  "captures": [
    {"target_id": "system", "kind": "whole_system", "video": "system.mp4"},
    {"target_id": "smoke", "kind": "solo_emitter", "video": "smoke.mp4"}
  ]
}
```

Extract temporal evidence:

```bash
python workspace/tools/extract_vfx_stills.py captures.json -o evidence --interval 0.5
```

The adapter uses the existing PASS Video Stills engine with its `vfx` preset and keeps every planned temporal sample. The resulting `vfx-stills-manifest.json` can then be registered:

```bash
python PASS/vfx.py register-captures --run workspace/vfx-authoring/boss-spawn \
  --manifest evidence/vfx-stills-manifest.json
```

## Model-authored phases

The controller emits the exact JSON shape expected for each model-authored phase:

```bash
python PASS/vfx.py template --run <run> --phase classification
python PASS/vfx.py template --run <run> --phase extraction
python PASS/vfx.py template --run <run> --phase validation
```

Submit them in order:

```bash
python PASS/vfx.py submit --run <run> --phase classification --input classification.json
python PASS/vfx.py submit --run <run> --phase extraction --input extraction.json
python PASS/vfx.py submit --run <run> --phase validation --input validation.json
```

### Classification

Classify what the isolated target **does visually** separately from how Unreal implements it:

- `effect_family`: smoke, trail, impact, flash, shockwave, ring, debris, fire, lightning, etc.
- `visual_role`: persistent volume, projectile trail, accent burst, climax, ground telegraph, transition, etc.
- `implementation.renderer`: sprite, ribbon, mesh, beam, light, decal, volume, etc.
- `implementation.simulation`: CPU, GPU, mixed, unknown.
- `implementation.motion_method`: event trail, curl noise, source history, velocity, scripted position, etc.
- `visual_style`: realistic, stylized, hybrid, or style_agnostic.

Do not infer implementation from appearance when the inventory/asset data can settle it.

### Extraction

Stage finished PASS cards under the run's `staging/library/.../recipes/<family>/` tree. A candidate names the isolated/whole-system evidence it came from, but the **card itself does not**. The staged card must already be self-contained and use the ordinary closed PASS Pattern/Drill/AP schema.

### Validation

Validation is visual and structural. It records which capture targets were inspected, observable checks, and near-misses excluded. Examples:

- a ring reaches full radius before the climax rather than snapping to size;
- smoke stays inside the intended footprint;
- impact frequency accelerates rather than remaining constant;
- a flash precedes a shockwave rather than firing simultaneously;
- the shockwave originates from the intended center;
- persistent layers are gone by the requested end time.

A failed candidate does not finish the run. Revise the effect/card evidence and resubmit extraction before trying validation again.

## Refinement boundary

The first version deliberately does **not** prescribe how the UE plugin must inspect Niagara internals, record viewport footage, isolate nested components, or compare images. Those mechanisms will be refined from real project work. The stable contract is the evidence sequence above: inventory, isolation, temporal capture, classification, self-contained extraction, visual validation.
