---
object_id: PAT_preserve_established_interface_conventions_when_they_carry_user_meaning
object_type: pattern
name: Preserve Established Interface Conventions When They Carry User Meaning
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
- systems
- terminology
- presentation
- compatibility
cross_links:
- rel: related_to
  target_object_id: PAT_use_the_defining_affordances_of_an_adopted_game_system
- rel: related_to
  target_object_id: PAT_design_rules_artifacts_for_learning_and_retrieval
reference:
  source_title: Designing TTRPGs For Dummies
  author: Martin Buinicki
confidence: high
references: []
variants: []
---

# Preserve Established Interface Conventions When They Carry User Meaning

## Pattern Rule
**IF** material is intended to operate inside an established game system or recognizable design family whose terminology or presentation conventions carry rules, workflow, or recognition value
**THEN** preserve those interface conventions or change them deliberately with a stated usability or design benefit
**ELSE** use the project's own terminology and presentation when inherited conventions do not help users understand or operate the material.

## Do
- Identify established terms that encode rules meaning, workflow expectations, or learned recognition rather than treating every familiar word as sacred branding.
- Preserve contributor or presentation conventions when they reduce interpretation cost for users of compatible material.
- Consult official style or contributor guidance when producing downstream material that must integrate with an established publication ecosystem.
- Distinguish interface compatibility from mechanical compatibility and from legal or license compliance; each can impose different constraints.
- Rename or reframe inherited terms when the existing convention creates a real usability, accessibility, or design problem and the replacement benefit exceeds the relearning cost.
- Test whether an existing user can recognize the intended operation of compatible material without translating unnecessary new vocabulary.

## Don't
- Rename established terms casually when the new language adds interface friction without changing the underlying decision.
- Treat visual mimicry or jargon as sufficient evidence that material is mechanically compatible.
- Preserve a confusing or harmful convention solely because it is traditional when the project can improve the interface intentionally.
- Treat publication style guidance as a substitute for understanding the actual rules the material must support.

## Checklist
- Inherited terminology retained by the design carries identifiable rules, workflow, or recognition value.
- Any changed convention has a stated benefit and an acknowledged relearning or compatibility cost.
- Compatible material follows required contributor or presentation guidance when such guidance is part of the operating environment.
- Interface, mechanical, and legal compatibility are not collapsed into one claim.
- Existing users can interpret the compatible material without unnecessary vocabulary translation.

## Notes
Terminology and presentation can function as part of a game's user interface. Familiar words, stat-block structures, headings, and contributor conventions let existing users transfer knowledge into new material. That does not make every inherited convention untouchable. The design question is whether the convention carries operational meaning worth preserving and, when it does, whether a change buys enough clarity or usability to justify the relearning cost. Interface compatibility should remain separate from the questions of mechanical behavior and legal permission.
