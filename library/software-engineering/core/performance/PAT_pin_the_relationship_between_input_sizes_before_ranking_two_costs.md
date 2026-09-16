---
object_id: PAT_pin_the_relationship_between_input_sizes_before_ranking_two_costs
object_type: pattern
name: Pin the Relationship Between Input Sizes Before Ranking Two Costs
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
- performance
- complexity
- data_shape
- algorithm_selection
- representation
cross_links:
- rel: related_to
  target_object_id: PAT_estimate_the_order_before_you_run_it
- rel: related_to
  target_object_id: PAT_choose_the_data_structure_for_the_dominant_access_pattern
- rel: related_to
  target_object_id: PAT_read_a_break_in_the_cost_curve_as_a_change_of_strategy
reference:
  source_title: Algorithms in a Nutshell
  author: George T. Heineman, Gary Pollice, Stanley Selkow
confidence: high
references: []
variants: []
---

# Pin the Relationship Between Input Sizes Before Ranking Two Costs

## Pattern Rule
**IF** two candidate methods have costs written in more than one measure of the input — items and the relationships between them, rows and the matches among them, documents and the terms they contain — and you are choosing between them
**THEN** establish how those measures relate on the data you will actually receive, before comparing the expressions, because both expressions are honest and which one is smaller is a property of the data rather than of the methods
**ELSE** where one cost is smaller for every relationship the measures could have, the ranking holds without measuring anything and the question is already settled.

## Do
- Rewrite the second measure in terms of the first for your data. A network of n nodes can carry anywhere from about n connections to about n squared of them, and substituting each end of that range into the two cost expressions is what turns two formulas you cannot compare into a ranking you can.
- Find the relationship at which the two are equal, rather than only testing the extremes. Two costs that differ in which measure carries the logarithm come out level at one particular density, and knowing that crossing point tells you which side your data sits on and how much margin you have; the extremes only tell you that a crossing exists somewhere between them.
- Let the same property choose the representation. Whatever decides which method wins usually also decides how the data should be held: the dense case wants the matrix whose cells are nearly all occupied, the sparse case wants the structure that stores only what exists, and choosing the representation for the other case penalises the method twice over.
- Take the relationship from real data rather than from what the type permits. A worldwide network of some sixteen hundred airports has room for over two and a half million direct connections and uses well under a tenth of them; sizing for the possible instead of the actual is how a structure ends up unable to hold the real problem at all.
- Ask again when the source of the data changes. The relationship belongs to where the input comes from, not to the problem statement, so a method chosen correctly for one feed can be the wrong one for another feed of exactly the same type.

## Don't
- Don't compare the expressions while treating one measure as a constant. Reading a cost written in two measures as though it concerned only the first silently assumes a density, and the assumption is invisible because no step in the comparison ever names it.
- Don't read a benchmark taken at one density as a ranking. Two implementations of a single algorithm — one built around a priority queue, one around a matrix — can differ by more than an order of magnitude in favour of the first on sparse data and by a similar margin in favour of the second on dense data. Nothing about the algorithm changed; the ranking belongs to the data.
- Don't assume the worst the type allows is the value you will see, or that the value you see now is the value you will keep seeing.
- Don't confuse this with choosing a structure for its memory behaviour. That question is about where the bytes sit and how they are walked, and it is settled by measuring the hierarchy rather than by counting operations; this one is settled before any of that, by a shape the data already has.

## Checklist
- How many distinct measures of the input does each cost expression use?
- On your data, how does the second measure relate to the first — nearer to linear in it, or nearer to its square?
- At what relationship are the two costs equal, and which side of it are you on?
- Does the representation you have chosen suit the same case the method suits?
- Is the relationship taken from data you actually receive, or from the maximum the type would allow?

## Notes
The trap this closes is that a single-parameter habit is usually correct and quietly fails here. Most cost expressions in ordinary code carry one measure, so comparing two of them is a matter of reading which grows faster, and the reflex transfers to expressions carrying two measures where it does not work — both can be correct, neither dominates, and the comparison has no answer at all until a fact about the data is supplied. The failure is silent because the missing fact is never written down; nobody states an assumption they did not know they were making.

The second measure is rarely free to choose, which is why it is worth identifying early. It is a property of the domain, fixed by whatever generates the input: a road network is sparse because places have few neighbours, a similarity graph over documents is dense because nearly everything relates to nearly everything a little. Reading that property off the domain is usually faster than measuring it, and it is the same property that will decide the representation, so the work is not spent twice.

There is a corollary about benchmarks. A comparison run on one body of data is a measurement at one relationship between the measures, and the ranking it produces extends exactly as far as that relationship holds. Two bodies of data of the same type, differing only in density, are two different experiments — and carrying a result from one to the other is the same error as leaving the parameter out of the comparison in the first place.
