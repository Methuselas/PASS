---
object_id: PAT_price_character_options_by_mechanical_leverage_and_constraint
object_type: pattern
name: Price Character Options by Mechanical Leverage
library_path:
- game-design
- characters
stage_binding: 0 design
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- balance
- characters
- costs
- point-economy
cross_links:
- rel: related_to
  target_object_id: PAT_keep_persistent_capability_dependencies_local_and_explicit
- rel: related_to
  target_object_id: PAT_price_drawbacks_by_the_constraint_they_actually_impose
- rel: related_to
  target_object_id: PAT_audit_character_economy_exchange_rates_across_creation_and_advancement
- rel: related_to
  target_object_id: PAT_treat_near_mandatory_role_options_as_role_infrastructure
- rel: related_to
  target_object_id: PAT_attach_persistent_costs_to_capability_gains
reference:
  source_title: GURPS Basic Set, Fourth Edition and GURPS Compendium I
  author: Steve Jackson, David L. Pulver, Sean M. Punch, and contributors
confidence: high
references: []
variants: []
---

# Price Character Options by Mechanical Leverage

## Pattern Rule
**IF** character options share a build currency or can substitute economically for one another
**THEN** price positive options by the breadth, frequency, downstream effects, configurability, and opportunity they create in play rather than by conceptual symmetry or dramatic wording
**ELSE** do not force nominally similar traits into equal prices when they do not buy comparable capability.

## Do
- Audit the leverage of broad traits. Count which skills, defenses, resources, derived values, defaults, future purchases, or other persistent capabilities change when the trait changes.
- Weight downstream effects by cadence and consequence rather than treating every dependency as equally valuable.
- Compare a broad purchase against representative narrower purchases that could produce the same intended concept.
- Reprice, narrow, or split a bundle when the broad option routinely dominates narrower alternatives that are supposed to remain viable.
- Provide intermediate bundles when the design needs a useful middle ground between one narrow capability and a very broad parent trait.
- Treat flexible configuration as capability. Selective activation, retargeting, reshaping, or switching between applications can create additional agency even when the peak numeric effect is unchanged.
- Compare the same intended character concept through more than one legal purchase path when the system permits substitutions.
- Re-run the leverage audit when supplements, modifiers, new traits, or advancement options expand what an existing purchase can influence.
- Distinguish purchase price from persistent operating cost; use price for comparative acquisition value and hand ongoing dependency, exposure, maintenance, or backlash to the system that owns persistent costs.

## Don't
- Price foundational attributes equally merely because their names are equally fundamental to the fiction.
- Assume a broad option is fair because its printed bonus is small when that bonus propagates through many high-cadence dependencies.
- Force every concept to choose between dozens of narrow purchases and one giant bundle when a thematic middle layer would create better differentiation.
- Price fixed and configurable versions of an effect identically when flexibility materially expands the user's choices.
- Preserve legacy prices after the dependency network changes enough that an option now buys substantially more or less than it did when first costed.
- Use a large one-time price as proof that a self-reinforcing capability is safe after purchase; acquisition value and persistent counterpressure are different questions.

## Checklist
- Each broad option has an identified downstream dependency set.
- Major dependencies are weighted by cadence and consequence rather than raw count alone.
- Representative broad and narrow purchase paths have been compared for at least one shared concept.
- No general-purpose trait is routinely the cheapest answer for several concepts intended to remain mechanically distinct without a deliberate reason.
- Intermediate bundles are tested against both broader and narrower alternatives when the design provides them.
- Configurability is included in the leverage audit when it expands meaningful choices.
- The audit is repeated after major additions to the option catalog or dependency graph.
- Persistent operating costs are not being used to conceal a plainly underpriced acquisition option, and acquisition price is not expected to replace an intended ongoing constraint.

## Notes
Point economies compare unlike fictional traits through one currency, so symmetry in description is not evidence of equal value. A broad attribute can be underpriced even when its number looks modest if it raises many skills, defenses, defaults, resources, or future purchases at once. The durable comparison is **what does this purchase change, how often does that matter, how much choice does it create, and what other legal purchase could achieve the same concept?** Intermediate bundles can relieve the common failure mode in which the only alternatives are a pile of narrow purchases or one dominant parent trait. This Pattern owns the leverage side of positive-option pricing; drawbacks, lifecycle exchange rates, role taxes, and ongoing capability costs are separate economic decisions.
