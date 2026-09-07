---
object_id: PAT_preserve_behavioral_compatibility_when_replacing_inherited_mechanics
object_type: pattern
name: Preserve Behavioral Compatibility When Replacing Inherited Mechanics
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
- compatibility
- migration
- editions
cross_links:
- rel: related_to
  target_object_id: PAT_use_the_defining_affordances_of_an_adopted_game_system
reference:
  source_title: Designing TTRPGs For Dummies
  author: Martin Buinicki
confidence: high
references: []
variants: []
---

# Preserve Behavioral Compatibility When Replacing Inherited Mechanics

## Pattern Rule
**IF** a design changes or replaces an inherited mechanic that existing characters, content, procedures, or player habits depend on
**THEN** inventory the migration burden and test whether the replacement preserves the capabilities, relative relationships, procedures, and play identity the project intends to keep
**ELSE** use a lighter compatibility check when the changed feature is isolated, optional, or deliberately outside the compatibility promise.

## Do
- Identify how frequently the inherited mechanic is used and what character data, published content, table procedures, house practices, or learned expectations depend on it.
- Separate numeric convertibility from behavioral compatibility. A formula that maps old values to new values is only one part of the migration question.
- Test representative legacy characters, rule interactions, and content through the replacement for capability preservation, relative power, executable procedure, and practical play identity.
- Record what existing users must convert, relearn, reinterpret, or abandon and compare that burden with the demonstrated benefit of the replacement.
- Demand more evidence for replacing high-frequency or identity-defining dependencies than for rare optional features.
- State explicitly when the project is choosing experiential repositioning over compatibility rather than describing the change as a transparent cleanup.
- Separate prospective migration from resolved history: apply the replacement procedure from an explicit transition point, and change already resolved campaign outcomes only when persistent state cannot remain coherent otherwise.
- When a new granular subsystem replaces a broad legacy capability, map established signature choices and relied-upon competence before assigning the remaining new specialization budget.

## Don't
- Treat the existence of a conversion table as proof that characters, capabilities, procedures, and table habits remain compatible.
- Assume a newer, cleaner, more unified, or more fashionable mechanic is automatically a better replacement for an established game.
- Hide migration cost by measuring only the new procedure after converted users and content have already absorbed the change.
- Call deliberate repositioning a compatibility-preserving revision when the replacement materially changes what existing play can do or how it feels.
- Replay or invalidate completed campaign events merely because a replacement rule would have produced a different historical result.

## Checklist
- The changed mechanic's downstream dependencies and activation frequency are known.
- At least one representative legacy character, content unit, or interaction has been executed through the replacement when compatibility matters.
- Capability, relative power, procedure, and play-identity preservation are checked separately from numeric conversion.
- Conversion, relearning, and abandonment costs are recorded and compared with the replacement's demonstrated benefit.
- Any intentional break in compatibility is named as such rather than hidden inside a claim of modernization or simplification.
- The migration plan states the transition point, what historical state is grandfathered, and which persistent results genuinely require conversion.

## Notes
Established systems accumulate more than numbers. Players learn probabilities and workflows, characters embody relationships among capabilities, published content assumes particular procedures, and groups develop habits around frequently used mechanics. Replacing a rare optional rule and replacing the engine through which most actions are understood therefore have very different migration costs. Compatibility is strongest when behavior and identity survive where the project intends them to survive, not merely when old values can be translated into new notation.

Persistent campaigns add a temporal compatibility boundary. A new procedure can govern future play without claiming the campaign always worked that way. When the replacement introduces finer specialization, preserve established signature competence first; when it changes a resolved historical outcome, prefer grandfathering unless the current persistent state would otherwise become incoherent.
