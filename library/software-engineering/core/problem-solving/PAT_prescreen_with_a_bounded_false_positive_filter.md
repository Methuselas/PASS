---
object_id: PAT_prescreen_with_a_bounded_false_positive_filter
object_type: pattern
name: Prescreen With a Bounded False-Positive Filter
library_path:
- software-engineering
- core
- problem-solving
stage_binding: 0 design
lane_fit: skill
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- algorithm_design
- probabilistic
- membership
- performance
cross_links:
- rel: related_to
  target_object_id: PAT_state_the_approximation_guarantee_you_actually_have
- rel: related_to
  target_object_id: PAT_choose_the_data_structure_for_the_dominant_access_pattern
reference:
  source_title: 'Algorithms in a Nutshell: A Practical Guide'
  author: George T. Heineman, Gary Pollice, Stanley Selkow
confidence: high
references: []
variants: []
---

# Prescreen With a Bounded False-Positive Filter

## Pattern Rule
**IF** every query is paying for an expensive lookup — a disk read, a network round trip, a full scan — and most of those lookups come back having found nothing
**THEN** put a compact probabilistic structure in front of the expensive check, sized so its false-positive rate is a chosen design parameter, and let a negative result from the structure skip the expensive path entirely
**ELSE** where a missed answer is tolerable, or the check it would guard is already cheap, the structure adds machinery without buying anything.

## Do
- Size the structure to the false-positive rate you can tolerate, not to the data you happen to have on hand today. The rate, the space given to the structure, and the number of entries it will hold trade directly against one another, and that trade is the entire design — get it wrong and either the space is wasted or the rate quietly grows past what callers assumed.
- Use several independent probes per entry rather than one. Membership sets or checks all of them together, and a single one coming back negative is enough to prove absence outright — that is the property every other guarantee here depends on.
- Reach for this to protect a genuinely expensive resource. It exists to make the "no" answer cheap; it is not a substitute for the "yes" answer's confirmation, which still has to run.
- Grow the structure to match the population you actually expect to feed it. More entries into a fixed-size structure raise its false-positive rate; one sized for a smaller population than it actually receives degrades quietly rather than failing loudly.

## Don't
- Don't use this where a false positive is unacceptable. It is a one-sided instrument — absence is certain, presence is only likely — and no amount of tuning removes that asymmetry, only shrinks it.
- Don't expect to remove one entry once it is added. The straightforward version has no way to clear one entry's contribution without risking another entry that shares it; if deletion matters, that calls for a different, larger structure, not a mode of this one.
- Don't skip the confirmation step on a positive result. A "maybe" from this structure is not a "yes" — code that treats it as one has silently turned a bounded, chosen error rate into an unbounded one.

## Checklist
- Is the check being guarded genuinely expensive enough to justify building this in front of it?
- Is a false positive tolerable (a wasted check) while a false negative is not (a missed answer)?
- Is the structure sized to the population it will actually hold, not the population it started with?
- Does every positive result still go through the real check before being trusted?

## Notes
The structure trades a small, fixed amount of space for lookups whose cost does not grow with the size of the collection, at the price of a one-sided error whose rate is a parameter you choose rather than a surprise you discover. That is the useful framing: this is not "an algorithm that is sometimes wrong," it is a deliberate, quantified trade of certainty for space, and the design work is entirely in choosing the rate rather than in the mechanism itself, which is fixed once the rate is set.

It belongs beside the family of decisions that accept a stated, bounded uncertainty in exchange for tractability — an approximation ratio proved over every input, a guarantee measured rather than argued. This one is neither; its guarantee is a single number fixed at construction time and independent of any particular input, which is what makes it composable in front of an otherwise-exact system without changing that system's own correctness.
