---
object_id: PAT_resume_a_failed_match_where_what_it_read_still_allows
object_type: pattern
name: Resume a Failed Match Where What It Read Still Allows
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
- string_search
- pattern_matching
- preprocessing
cross_links:
- rel: related_to
  target_object_id: PAT_detect_a_degrading_run_and_switch_to_a_bounded_method
- rel: related_to
  target_object_id: PAT_estimate_the_order_before_you_run_it
- rel: related_to
  target_object_id: PAT_predict_cost_from_counted_operations_and_measured_unit_costs
reference:
  source_title: An Introduction to the Analysis of Algorithms
  author: Robert Sedgewick, Philippe Flajolet
confidence: high
references: []
variants: []
---

# Resume a Failed Match Where What It Read Still Allows

## Pattern Rule
**IF** a search tries a pattern at successive positions of a sequence, and a try can match part of the pattern before it fails
**THEN** work out in advance, from the pattern alone, which later positions each partial match or mismatching element rules out, and move straight to the first position still possible — without re-reading input that the failed try has already read
**ELSE** where partial matches stay short, as in random-like data, trying every position from scratch costs little more than one comparison per input element, and the precomputation pays only if it lets the search skip positions outright.

## Do
- Precompute how the pattern overlaps itself. For each length of matched prefix, the longest shorter prefix that is also a suffix of it is where the try can resume, because the input just read already matches that much; the input position then never moves backward. On ten million characters of `a` with a `b` every thousand, searching for 99 `a`s followed by `b` from scratch at every position took 95 comparisons per character and 362 ms; resuming from the overlap took 2.9 and 10 ms.
- Let a mismatched element skip positions outright when the alphabet is large. Compare from the pattern's end, and move the pattern by how far the input element under its last position lies from the pattern's end — the full pattern length when that element does not occur in the pattern at all. On ten million random letters with a 16-letter pattern this made 0.086 comparisons per character and took 1.8 ms, against 1.04 and 7.6 ms from scratch; on a four-letter alphabet, 0.28 and 8.9 ms against 1.33 and 30.4.
- Search for several patterns in one pass with one automaton. Put the patterns in a trie and give each dead end the same treatment as a single pattern's overlap: a failure resumes at the longest pattern prefix that ends where the input stands, rather than returning to the root and backing up the input.
- Expect the plain search to hold up on random-like input and measure before replacing it. On random letters it made 1.04 comparisons per character; on random bits it made 2.00 whatever the pattern, and resuming from the overlap cut that to 1.70–1.75 without saving any time (39–40 ms).

## Don't
- Don't take a skip that uses one element per failure as safe on repetitive input. It forgets everything else the failed try matched. On the same run-filled text, searching for `b` followed by 99 `a`s, the skip made 90 comparisons per character and took 328 ms, while resuming from the overlap made 1.1 and took 4.7 ms.
- Don't benchmark a pattern search only on random text. The costs that separate these methods — 95 and 90 comparisons per character above, against about one — appear only on input with long partial matches, and a random-text benchmark ranks all three methods as nearly equal.

## Checklist
- Can the input contain long stretches that partially match the pattern?
- Does the search resume from the pattern's overlap with itself, so input is never re-read?
- Is the alphabet large enough for a mismatched element to skip whole pattern lengths, and is the input safe from the runs that defeat that skip?
- Are several patterns searched in one automaton pass rather than one pass each?
- Was the choice measured on repetitive input as well as random input?

## Notes
The from-scratch search throws away information. When a try matches part of the pattern and then fails, the matched input is already known to equal a prefix of the pattern. Which later positions can still succeed is therefore a question about the pattern alone, and it can be answered once, before the search starts. Every variant here stores that answer in a table indexed by what the failure saw: the matched length, the mismatching element, or the trie node where the search stopped.

The variants save in different ways, so they fail in different places. Resuming from the overlap bounds the total work by a small multiple of the input length whatever the input, but on random-like data it saves almost nothing, because partial matches there are short anyway. The mismatched-element skip is the fastest on random text over a large alphabet, because most failures move the pattern a full length. Its guarantee is weaker, though, because a single element cannot remember a long partial match.
