---
object_id: PAT_compose_an_associative_step_by_doubling
object_type: pattern
name: Compose an Associative Step by Doubling
library_path:
- software-engineering
- core
- performance
stage_binding: 0 design
lane_fit: skill
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- algorithm_design
- exponentiation
- repeated_squaring
- complexity
cross_links:
- rel: related_to
  target_object_id: PAT_estimate_the_order_before_you_run_it
- rel: related_to
  target_object_id: PAT_choose_the_path_method_by_what_the_weights_can_be
reference:
  source_title: Introduction to Algorithms
  author: Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, Clifford Stein
confidence: high
references: []
variants: []
---

# Compose an Associative Step by Doubling

## Pattern Rule
**IF** you need the effect of applying or combining the same step a large number of times — a power, a transform applied k times, routes of up to k steps — and two applications can be combined into one object of the same kind by an operation that does not care how applications are grouped
**THEN** combine the step with itself repeatedly so each combination doubles the count covered, and read the target count from its binary digits, so k applications cost a number of combinations proportional to the logarithm of k
**ELSE** where combining two applications does not produce something of the same kind, or regrouping changes the result, there is nothing to double and the step has to be applied one at a time.

## Do
- Establish associativity before regrouping. It is what makes combining two combined halves equal to applying the step four times in order. Extending cheapest routes by one link — take the minimum over intermediate points of a route cost plus a link cost — is associative, so routes of up to 63 links through 64 points came from 6 squarings instead of 62 one-link extensions, and the two tables were identical.
- Walk the binary digits of the count from the top: square what you have at each digit, and combine once more with the single step when the digit is 1. Raising 7 to the millionth power modulo a large prime this way took 27 multiplications and 11 microseconds; multiplying one step at a time took 1,000,000 multiplications and 46 milliseconds, with the same result.
- Let the doubling overshoot when extra applications cannot change the answer. Cheapest routes with more links than there are points are no cheaper when no loop has negative cost, so squaring until the count covered first exceeds the number needed gives the exact table without tracking the digits at all.

## Don't
- Don't overshoot when every application changes the result. A power has to reach its exponent exactly, which is why that case reads the digits of the count instead of squaring until it is large enough; decide which kind of problem you have before choosing between the two.

## Checklist
- Does combining two applications give an object of the same kind as one application?
- Is that combination associative?
- Is the count large enough that logarithmically many combinations matter?
- Do extra applications leave the answer unchanged, so that overshooting is safe, or must the count be hit exactly?

## Notes
The move trades a count for its length. A step repeated a million times becomes twenty combinations, because each combination represents twice as many applications as the one before it, and the binary digits of any count say which of those doublings to keep. Nothing about the individual step gets cheaper; the saving is entirely in how few combinations are needed, which is why it depends on nothing but the combining operation being indifferent to grouping.

That condition is also why the technique turns up in places that look unrelated: raising a number to a power under a modulus, multiplying matrices whose entries are route costs, and applying any transform that can be represented as a composable object are the same computation with different operations plugged in. Recognising that a repeated step can be packaged as such an object is most of the work; the doubling itself is short, tight code.
