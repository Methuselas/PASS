---
object_id: PAT_read_a_break_in_the_cost_curve_as_a_change_of_strategy
object_type: pattern
name: Read a Break in the Cost Curve as a Change of Strategy
library_path:
- software-engineering
- core
- performance
stage_binding: 4 final
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- performance
- measurement
- benchmarking
- cost_model
- abstraction
cross_links:
- rel: related_to
  target_object_id: PAT_estimate_the_order_before_you_run_it
- rel: related_to
  target_object_id: PAT_reproduce_the_real_context_before_believing_a_microbenchmark
- rel: related_to
  target_object_id: PAT_let_measurement_decide_what_to_tune
reference:
  source_title: Algorithms in a Nutshell
  author: George T. Heineman, Gary Pollice, Stanley Selkow
confidence: high
references: []
variants: []
---

# Read a Break in the Cost Curve as a Change of Strategy

## Pattern Rule
**IF** you are relying on the cost of an operation you did not write — a language operator, a library call, a runtime primitive — and that cost is assumed rather than measured
**THEN** time it across a wide range of input sizes and read the shape of the result, treating any break in the curve as the implementation changing strategy or representation at that size
**ELSE** where the operand is held in a representation that cannot grow, the cost is genuinely fixed and the sweep has nothing to find.

## Do
- Sweep sizes across orders of magnitude rather than a cluster of nearby ones. The breaks sit at particular sizes, and a range that straddles none of them yields a clean curve that is accurate and tells you nothing about the sizes you did not visit.
- Read a break as a threshold somebody chose. Measured sorting times that fit one curve below forty elements and a different one above it are not an artifact of the timing: they locate the cutoff in a hybrid implementation that switches to a simpler method on small inputs, and the cutoff is a fact about the library you are calling.
- Suspect the representation when a break sits near a machine boundary. A multiplication whose cost shifts between sixty-four and sixty-five of something has crossed from operands held in one machine word to operands held in several, and every size above that point is paying a different price for what reads in the source as the same operator.
- Distrust "this operation is constant time" wherever its operand can grow. Adding two integers is constant only because a fixed-width representation refuses to grow; the identical addition over arbitrary-precision numbers is linear in the digits, and nothing at the call site distinguishes the two.
- Use the sweep where you cannot read the implementation at all. A closed library, a language runtime, or a just-in-time compiler will not tell you which method it selects at which size, and the curve is the only instrument that reaches them — a rise that flattens into three distinct regimes is the implementation announcing that it has three strategies.
- Phrase the assumption as a hypothesis before measuring it, so the measurement can refute it. "The cost of this operation does not depend on the magnitude of its operand" is a claim a sweep can falsify; "this operation is fast" is not.

## Don't
- Don't average a break away. Fitting one curve through a range that contains a discontinuity produces a function that matches nowhere and hides the one thing the sweep was run to find.
- Don't extend a measured cost model past the largest size you measured. The next break is, by construction, not in the data you have.
- Don't read the break as identifying the new strategy. It tells you the size at which behaviour changed and says nothing about what it changed to; confirming that against the implementation or its documentation is a separate step, and it is often available — the cutoffs in a widely used sort routine are described in the paper its source comments cite.
- Don't confuse this with checking whether a benchmark is representative. That question is whether the measured context resembles the real one; this question is whether the cost model you are carrying in your head has a boundary inside the range of sizes you will actually pass.

## Checklist
- Which operations does this code treat as cheap, and did you write any of them?
- Does the measured range span the sizes the program will see, and at least an order of magnitude beyond?
- Is there a break in the curve, and does it sit near a size the machine or the library would care about?
- Is the constant-time claim true for every operand size, or only while the representation stays fixed?
- What would falsify the cost assumption, and did the sweep actually test it?

## Notes
The move is worth naming because the alternative is invisible. A cost assumption about a borrowed operation is rarely written down and never checked, so it survives until a production input crosses a boundary nobody knew was there — and the symptom is a program that was fast for two years and is now slow, with no change to the code that would explain it.

Two assumptions fail this way often enough to be worth testing by default. The first is that an operation's cost does not depend on the magnitude of its operands, which holds exactly as long as the operands fit the representation the language chose and fails silently the moment the language quietly promotes them to something that grows. The second is that one spelling in the source means one implementation underneath, which arbitrary-precision arithmetic, hybrid sort routines, and small-size optimisations in containers all violate deliberately and for good reasons.

The sweep is cheap in a way the rest of performance work is not. It needs no profiler, no instrumentation of the program, and no access to the implementation; it needs a loop over sizes and a plot. That it is so often skipped has less to do with cost than with the assumption never having been stated as a claim in the first place.
