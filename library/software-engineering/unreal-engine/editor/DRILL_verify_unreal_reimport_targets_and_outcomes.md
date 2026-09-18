---
object_id: DRILL_verify_unreal_reimport_targets_and_outcomes
object_type: drill
name: Verify Unreal Reimport Targets and Outcomes
library_path:
- software-engineering
- unreal-engine
- editor
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- editor_tools
- reimport
cross_links:
- rel: teaches
  target_object_id: AP_reimport_an_unreal_asset_from_an_explicit_target
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
target_skill: Resolve explicit editor targets and verify asset reimport outcomes
---

# Verify Unreal Reimport Targets and Outcomes

## Practice Task
Produce a disposable editor fixture that resolves declared selection targets, reimports an existing asset after its source changes, and records rejection cases.

## Target Skill
Practise `AP_reimport_an_unreal_asset_from_an_explicit_target` by separating target resolution, import completion and refreshed-data verification.

## Setup
An Unreal editor C++ toolchain, a disposable project, a small supported source file and its imported asset. Keep the input, asset and test outputs separate from working game assets.

## Instructions
1. State the actor and component cardinality policy. Exercise zero, one and multiple actor selections; record targets and returned reasons.
2. Create or import the fixture asset from its original source and record its relevant data.
3. Change a distinguishable source value, reimport through the callable operation, and record the returned outcome and actual refreshed data.
4. Attempt a null asset, an asset without a supported reimport source, and a missing required source. Record each reason and the before/after data of any valid fixture assets involved.
5. Record whether dialogs, unrelated commands, save operations or restoration occurred. If a keyboard entry point is exercised, record its key phase and number of callback executions.
6. Explain the difference between selecting an actor instance and reimporting its shared asset. Retain the build result and observations.

## Success Check
- The fixture builds and runs; a code listing or predicted change is insufficient.
- Selection outcomes enforce the stated policy, including the multiple-selection case.
- Actual asset data changes to match the edited source; successful dispatch alone does not qualify.
- Rejected preflight cases return useful reasons; valid fixture assets retain their prior data.
- Claims about keyboard routing, modal behavior, persistence and restoration match the interfaces exercised.
- The explanation identifies shared-asset impact rather than implying only one actor instance changed.

## Common Failures
- Returning the last actor despite a single-selection contract.
- Passing a component's null asset to the importer.
- Treating an import request as proof of refreshed content.
- Opening a file-picker dialog during unattended execution.
- Claiming undo or saving without observing either.

## Notes
A small distinguishable source change makes completion observable. Unsupported and missing-source cases distinguish a reliable boundary from a convenience wrapper that only invokes the importer.
