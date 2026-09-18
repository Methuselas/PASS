---
object_id: PAT_reimport_unreal_assets_through_validated_sources
object_type: pattern
name: Reimport Unreal Assets Through Validated Sources
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
cross_links: []
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Reimport Unreal Assets Through Validated Sources

## Pattern Rule
**IF** an Unreal editor tool needs to refresh an existing imported asset from its source files
**THEN** validate the asset and source policy, delegate to Unreal's registered reimport machinery, and verify the resulting asset instead of treating dispatch as completion.

## Do
- Resolve the referenced asset from the intended component or accept an explicit asset argument.
- Use `FReimportManager` rather than duplicating the asset format's importer.
- Check reimport capability and source filenames before an unattended call; reject absent or missing required sources without opening a replacement-file dialog.
- Choose interactive missing-file handling deliberately. An interactive validation-and-reimport convenience call is not a machine-readable result contract.
- For automation, suppress prompts and return the engine-reported outcome with failure detail. Wait for completion when using an asynchronous import path.
- Read back the asset data that the operation was intended to refresh and identify shared consumers affected by that asset.
- State restoration and persistence separately: an asset reimport is not made reversible or saved merely by wrapping a call in a transaction.

## Don't
- Don't pass a null mesh reference just because its component exists.
- Don't report a void batch-dispatch call as confirmed successful reimport.
- Don't promise atomic rollback across import side effects without verifying it.

## Checklist
- Is there a registered importer and are required source files available?
- Can unattended callers obtain an outcome without a modal dialog?
- Does asset readback show the intended source change?
- Are save and restoration claims supported separately?

## Notes
The component supplies a reference; the reimport manager supplies format-specific work. Keep target resolution separate from import execution so the same primitive can serve a viewport command, Blueprint utility or remote editor caller. Engine-reported completion still needs objective-specific readback.
