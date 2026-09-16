---
object_id: PAT_keep_the_order_of_equal_keys_when_it_carries_information
object_type: pattern
name: Keep the Order of Equal Keys When It Carries Information
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
- sorting
- ordering
- stability
- data_modelling
cross_links:
- rel: related_to
  target_object_id: PAT_choose_a_problem_representation_before_solving
- rel: related_to
  target_object_id: PAT_detect_a_degrading_run_and_switch_to_a_bounded_method
reference:
  source_title: Algorithms in a Nutshell
  author: George T. Heineman, Gary Pollice, Stanley Selkow
confidence: medium
references: []
variants: []
---

# Keep the Order of Equal Keys When It Carries Information

## Pattern Rule
**IF** you are about to reorder a collection whose current arrangement was not arbitrary
**THEN** decide explicitly whether the existing order of elements your comparator calls equal has to survive, and choose a method that guarantees it when the answer is yes
**ELSE** where the current arrangement carries nothing — it arrived in whatever order the source produced — any method will do and the question costs nothing to have asked.

## Do
- Ask what the comparator ignores. Stability is only ever about the fields you are *not* ordering by, so the question is what information lives in the current arrangement that the key does not mention, and whether anything downstream reads it.
- Build a multi-key ordering by sorting on the weakest key first and the strongest last, with a method that preserves ties. Flights already in departure-time order, sorted again by destination with ties preserved, come out grouped by destination and in time order within each group — and no comparator had to mention both fields.
- Say it in the interface rather than relying on the implementation you happen to call. A caller depending on preserved order is depending on a property, and a property nobody wrote down survives exactly until somebody swaps the sort for a faster one.
- Expect to pay for the guarantee. The methods that provide it generally want extra storage proportional to the input, which is a real cost and the reason the faster in-place methods do not offer it.
- Check the language before assuming either way. Some standard libraries guarantee the property, some offer it as a separate named operation, and some make no promise at all while appearing to preserve order on the inputs you happened to try.

## Don't
- Don't infer the guarantee from observed behaviour. A method that makes no promise may preserve order on small inputs, on nearly ordered inputs, or on the particular data in front of you, and then stop doing so when a size threshold inside it switches to a different strategy.
- Don't reach for a compound comparator when the weaker key is already in place. Ordering by two fields at once is correct and is more code, more that can be got wrong, and a comparator that has to be kept in step with a second sort elsewhere.
- Don't assume the arrangement is meaningless because nobody documented it. The order a collection arrives in is frequently the order of insertion, of arrival, or of a previous sort, and each of those is information somebody may already be reading.

## Checklist
- What does the comparator ignore, and does anything downstream depend on it?
- Was the current arrangement produced by something, or is it arbitrary?
- Does the method you are calling promise to preserve ties, or have you only observed that it does?
- If you need several keys, is there an existing ordering you can build on rather than restate?
- Is the requirement written where a future caller swapping the implementation would see it?

## Notes
This is a small decision with a silent failure mode, which is the combination that earns it a place. Nothing fails when a tie-preserving requirement is violated: the collection is correctly ordered by the key that was asked for, every element is present, and the property that broke was one nobody stated. It surfaces later as a report whose rows are shuffled within each group, or a user interface whose secondary ordering drifts between runs, and by then the sort and the symptom are far apart.

The composition trick is the part worth remembering, because it inverts the obvious approach. Ordering by several keys reads like a job for a comparator that knows all of them, and the alternative — one pass per key, weakest first, each preserving what the last pass established — needs no comparator to know more than one field and composes with orderings that were established elsewhere, including ones established before this code ran.
