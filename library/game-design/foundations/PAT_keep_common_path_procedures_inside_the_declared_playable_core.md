---
object_id: PAT_keep_common_path_procedures_inside_the_declared_playable_core
object_type: pattern
name: Keep Common-Path Procedures Inside the Declared Playable Core
library_path:
- game-design
- foundations
stage_binding: 0 design
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- core
- completeness
- modules
- packaging
cross_links:
- rel: related_to
  target_object_id: PAT_define_completion_against_a_living_game_design_document
reference:
  source_title: Designing TTRPGs For Dummies
  author: Martin Buinicki
confidence: high
references: []
variants: []
---

# Keep Common-Path Procedures Inside the Declared Playable Core

## Pattern Rule
**IF** a product or rules package is presented as a complete playable core
**THEN** keep every common-path procedure executable from that declared core surface, allowing supplements to broaden options or deepen detail without becoming undisclosed requirements for ordinary resolution
**ELSE** state the external requirement as part of the actual base configuration rather than presenting the package as self-sufficient.

## Do
- Trace ordinary procedures such as attacks, recovery, powers, travel, or other common branches through to their terminal results using only the declared core.
- Treat a supplement that is required to finish an ordinary branch as part of the real base dependency set even when it is physically separate.
- Let supplements add options, detail, special cases, or new domains without making the previously complete common path depend on them retroactively.
- Test the core with external books, modules, and references removed so hidden dependencies become visible.
- Update the declared base configuration when a dependency is intentionally promoted into required play.

## Don't
- Call a product complete when an ordinary attack, spell, recovery, or other common procedure requires an unbundled book or hidden module to reach a result.
- Treat physical separation as proof that a supplement is optional.
- Hide a required dependency behind cross-reference language that assumes the user already owns another product.
- Preserve the marketing claim of a self-contained core after the design intentionally makes another module mandatory.

## Checklist
- Representative common-path procedures reach terminal results using only the declared playable core.
- Removing external supplements does not strand an ordinary branch in unresolved state.
- Any external material required for base play is declared as part of the actual base configuration.
- Supplements can be absent without invalidating the procedures the core claims to contain.
- A newly mandatory dependency causes the core declaration to change rather than remaining hidden.

## Notes
A complete core is a dependency claim, not a page-count claim. Supplements can legitimately expand a game, but ordinary play should not discover halfway through resolution that the advertised core quietly depends on another book. If an external module becomes required, the honest repair is to change the base configuration or restore the common path to the core.
