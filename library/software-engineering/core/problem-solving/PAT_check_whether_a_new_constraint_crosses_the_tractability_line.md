---
object_id: PAT_check_whether_a_new_constraint_crosses_the_tractability_line
object_type: pattern
name: Check Whether a New Constraint Crosses the Tractability Line
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
- intractability
- requirements
- estimation
cross_links:
- rel: related_to
  target_object_id: PAT_check_whether_the_problem_is_a_known_hard_one_in_disguise
- rel: related_to
  target_object_id: PAT_price_a_requirements_change_instead_of_absorbing_it
reference:
  source_title: Algorithms
  author: Sanjoy Dasgupta, Christos Papadimitriou, Umesh Vazirani
confidence: high
references: []
variants: []
---

# Check Whether a New Constraint Crosses the Tractability Line

## Pattern Rule
**IF** a requirement is being added, tightened, or generalised on a problem you can currently solve efficiently
**THEN** check whether the amended statement is still that problem or has become one of the intractable ones before agreeing to it, because the two sit far closer together than the size of the wording change suggests.

## Do
- Carry a few of the neighbouring pairs, since they are what calibrate the intuition. Finding the cheapest route through a network is routine and finding the longest is not. Connecting every site as cheaply as possible is routine; visiting every site once as cheaply as possible is not. Two conditions per requirement is routine and three is not. Answers that may be fractional are routine and answers that must be whole numbers are not. Pairing two groups is routine and pairing three is not.
- Notice that the wording changes by a word or two in every one of those, which is why the size of the edit is worthless as an estimate. The relevant question is never how much text changed but whether the amended problem is still the one you had a method for.
- Ask what the requirement is protecting before pricing it. A demand for whole numbers usually comes from something real that cannot be half-allocated, and naming that thing is what makes a weaker form of the requirement discussable at all.
- Report the finding as a choice rather than a refusal. The requirement can be had at the price of exact answers, or of a limit on input size, or of a method that is usually fast — and the requester is entitled to pick, having been told.

## Don't
- Don't estimate a constraint's cost from how naturally it reads. The ones that flip a problem read like clarifications — of course the answer should be a whole number, of course each site should be visited once — and reading naturally is a property of the sentence, not of what it demands.
- Don't assume a generalisation costs proportionally more than the special case. Moving from two groups to three, or from a tree to a general graph, is not a bigger version of the same job; it can be a different problem with no efficient method at all.
- Don't take the reverse for granted either. Dropping a constraint sometimes moves a problem back across the line and sometimes changes nothing, so a relaxation offered as a concession is worth checking before it is accepted as one.

## Checklist
- What exactly does the amended statement ask for, written without the domain's vocabulary?
- Is that still the problem your current method solves?
- Which known pair is this closest to, and which side does the amendment land on?
- What is the requirement protecting, and is there a weaker form that protects it?
- Has the requester been given the choice, or only the requirement?

## Notes
The reason this needs to be a deliberate check is that every instinct available for estimating a change points the wrong way. A small edit to a sentence suggests a small change in difficulty; a requirement that sounds like common sense suggests it costs nothing; a generalisation suggests a proportionally larger version of the same work. All three are unreliable here, and there is no feel for it that develops without the pairs being seen side by side, because nothing in the surface of the two statements distinguishes them.

The pairs are also the cheapest way to hold the knowledge. Nobody needs the classification theory to act on this — what is needed is the reflex that a requirement about whole numbers, or about visiting everything once, or about a third dimension being added to a pairing, is a requirement that deserves an hour of checking before it is agreed rather than after.
