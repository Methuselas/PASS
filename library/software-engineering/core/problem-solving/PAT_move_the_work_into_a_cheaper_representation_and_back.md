---
object_id: PAT_move_the_work_into_a_cheaper_representation_and_back
object_type: pattern
name: Move the Work Into a Cheaper Representation and Back
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
- representation
- performance
- transformation
cross_links:
- rel: related_to
  target_object_id: PAT_choose_a_problem_representation_before_solving
- rel: related_to
  target_object_id: PAT_estimate_the_order_before_you_run_it
reference:
  source_title: Algorithms
  author: Sanjoy Dasgupta, Christos Papadimitriou, Umesh Vazirani
confidence: high
references: []
variants: []
---

# Move the Work Into a Cheaper Representation and Back

## Pattern Rule
**IF** an operation is expensive in the form your inputs arrive in and outputs must leave in, and cheap in some other form
**THEN** treat converting there, operating, and converting back as one candidate algorithm, and adopt it only when both conversions together cost less than doing the work in place.

## Do
- Separate the form the interface fixes from the form the work prefers. A polynomial given by its coefficients is expensive to multiply and a polynomial given by its values at enough points is multiplied pointwise, but callers hand you coefficients and expect coefficients back, so the value form is available only as an interior stage.
- Price all three legs before believing the middle one. The cheap operation is not the algorithm; the algorithm is convert plus operate plus convert back, and a conversion no faster than the original work leaves you exactly where you started.
- Make the round trip exact, or state what it costs. Conversions that lose information turn a performance decision into a correctness decision, and a scheme that returns an approximation must say so where callers can see it.
- Reuse one mechanism for both directions where the structure permits. The transform that carries values one way frequently carries them back with one parameter inverted, which halves the code that has to be right and removes a whole class of asymmetry bug.
- Amortise the conversion over more work when a single operation cannot justify it. Several operations performed in the cheaper form pay for one round trip between them, which can turn a losing trade into a winning one without changing either conversion.

## Don't
- Don't confuse this with picking the representation you will solve in. That decision keeps one form throughout; this one commits to two and to the cost of moving between them, and it is worth doing precisely when the interface will not let you keep the better form.
- Don't let an elegant transform hide an unpriced one. The direction that gets designed carefully is usually the outbound one, and the return trip inherits whatever is left over — which is where the cost that sinks the scheme tends to sit.
- Don't adopt the round trip for a single small input. The conversions carry constants that the growth rates hide, and below some size the direct method wins on every input you will actually see.

## Checklist
- Which form do the inputs and outputs have to be in, and is that the form the work is expensive in?
- What does each conversion cost, and what does the operation cost in each form?
- Do all three legs together beat doing the work directly, and above what input size?
- Is the round trip exact, and does one mechanism serve both directions?

## Notes
The shape recurs far outside any one algorithm: the same reasoning underlies solving a differential equation by transforming it into an algebraic one, multiplying by adding logarithms, and rotating coordinates so a hard geometric constraint becomes an easy one. In every case the interesting content is the same three-line budget — cost out, cost of the easy operation, cost back — and the discipline is refusing to be impressed by the middle line on its own.

There is a useful geometric reading when the two forms are related by a linear map. The forward conversion is then a change of basis, the operation is performed along the new axes where it decouples, and the return is the inverse rotation. Seeing it that way explains why the two directions so often share one mechanism: an inverse rotation is the same rotation with the angle negated, and the corresponding computational fact is that the return transform is frequently the outbound one with a single parameter replaced by its reciprocal.
