---
object_id: PAT_choose_the_collision_scheme_by_whether_you_delete
object_type: pattern
name: Choose the Collision Scheme by Whether You Delete
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
- hashing
- data_structures
- deletion
- load_factor
cross_links:
- rel: related_to
  target_object_id: PAT_choose_the_data_structure_for_the_dominant_access_pattern
- rel: related_to
  target_object_id: PAT_sample_a_split_point_you_cannot_afford_to_compute
- rel: related_to
  target_object_id: PAT_measure_how_much_your_index_actually_prunes
reference:
  source_title: Introduction to Algorithms
  author: Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, Clifford Stein
confidence: high
references: []
variants: []
---

# Choose the Collision Scheme by Whether You Delete

## Pattern Rule
**IF** you are choosing how a hash table handles two keys landing in one slot — a separate chain hanging off each slot, or probing onward for another slot inside the table itself
**THEN** decide it from whether keys are ever removed and how full the table will run, because probing's advantage rests on a bound that deletion takes away
**ELSE** where the set of keys is fixed and known before the table is built, neither scheme is the question and a structure built for that exact set beats both.

## Do
- Ask whether anything is ever removed, and ask it first. A table that only grows is the case where probing is at its best: everything lives in one allocation, there is no per-entry pointer to follow or to store, and a lookup walks memory in order instead of chasing links.
- Understand precisely what a removal costs a probing table. You cannot simply empty the slot, because a later search for some different key probes along its own sequence, meets the hole, and concludes the key is absent while it sits further along. The usual repair is to mark the slot as vacated rather than empty, so searches pass through it and insertions may reuse it.
- Notice what that repair costs, because it is the whole decision. Once vacated markers accumulate, search time is governed by how many of them there are rather than by how full the table is — and a bound in terms of how full the table is was the reason to choose probing. The scheme still works and the property you selected it for is gone.
- Keep the occupancy below one when probing, and treat that as a hard ceiling rather than a guideline. Every entry occupies a slot, so the table cannot hold more entries than it has slots, and cost climbs steeply as it approaches full. Chaining has no such ceiling; it degrades smoothly instead, which is the right shape when you cannot predict the population.
- Let the probe sequence scatter rather than march. Trying the next slot along is the easiest thing to implement and builds long unbroken runs, and a run that grows becomes more likely to grow, because every key landing anywhere within it extends it. Sequences that depend on the key throughout, rather than only at their start, are what break that feedback. Measured on a million-slot table with random keys, stepping to the next slot cost 5.5 probes per hit and 50 per miss at 90% full, 190 per miss at 95% and over 4,000 at 99%; a step computed from the key cost 2.6 and 10 at 90%, 20 per miss at 95% and 100 at 99%. At half full the two differed by less than one probe.
- Make the slot index depend on every part of the key. Where it depends on only some of the key, whatever structure the keys already have survives into the index — related identifiers, timestamps sharing a prefix, or ids sharing a suffix then collide in exactly the way the table exists to avoid.

## Don't
- Don't read a table's measured speed after heavy deletion as its steady state. Vacated slots are not reclaimed by ordinary use, so the cost drifts upward over the life of the process, and the fix is to rebuild the table rather than to tune anything.
- Don't let the table's size quietly discard most of the key. Sizing the table to a round binary figure and taking the remainder keeps only the lowest bits of the key and throws the rest away; either the size or a deliberate mixing step has to bring the whole key to bear, and which of the two you use matters far less than that one of them is there.
- Don't choose probing for its memory layout and then run it near full. The compactness argument and the occupancy argument point in opposite directions, and a table sized so tightly that it runs at high occupancy has spent its advantage buying its own worst case.
- Don't assume the language's default is a decision somebody made for your workload. The standard container picks one of these schemes, and the choice is a reasonable default rather than an answer about a table that deletes heavily, runs nearly full, or holds a key type with strong internal structure.

## Checklist
- Are keys ever removed, and if so, roughly what fraction over the life of the table?
- If the table probes, what happens to a search once removals have accumulated, and what rebuilds it?
- What occupancy will this run at, and is the maximum population known?
- Does the index depend on the whole key, or only the part that survives the sizing?
- Was the scheme chosen, or inherited from whichever container was reached for first?

## Notes
The trap here is that the two properties trade against each other silently. Probing is chosen for compactness and locality, and both are real; the cost guarantee that makes it safe to choose is stated in terms of occupancy, and removals quietly replace occupancy with something else as the governing quantity. Nothing announces the substitution — no operation fails, no measurement at the moment of the change looks different, and the drift only becomes visible over a long-running process well after the design decision is forgotten.

The advice about bringing the whole key to bear is worth separating from the specific technique usually attached to it. Older treatments reach the goal by choosing a table size with no common structure with the keys, which works and constrains the size to awkward values. Current practice more often keeps a convenient size and puts a mixing step ahead of the index so that every input bit influences every output bit. These are two routes to one requirement, and the requirement is the durable part: an index computed from a fraction of the key inherits whatever regularity the keys have.

Where this decision genuinely does not arise is the case of a key set fixed before the table is built. Knowing every key in advance permits an arrangement with no collisions at all, and the effort of choosing between collision schemes is then spent on a problem you do not have.
