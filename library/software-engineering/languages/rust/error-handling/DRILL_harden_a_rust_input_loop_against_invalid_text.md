---
object_id: DRILL_harden_a_rust_input_loop_against_invalid_text
object_type: drill
name: Harden a Rust Input Loop Against Invalid Text
library_path:
- software-engineering
- languages
- rust
- error-handling
stage_binding: 2 block
lane_fit: teach
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- rust
- result
- parsing
- input
- practice
cross_links:
- rel: teaches
  target_object_id: PAT_turn_rust_parse_failures_into_loop_control
reference:
  source_title: The Rust Programming Language
  author: Steve Klabnik and Carol Nichols
confidence: medium
references: []
variants: []
target_skill: PAT_turn_rust_parse_failures_into_loop_control
---

# Harden a Rust Input Loop Against Invalid Text

## Practice Task

Change a line-oriented Rust program that currently panics on a failed numeric parse so it survives malformed input, requests another value, and still exits through its normal success condition.

## Target Skill

Use a parser's `Result` to distinguish a usable typed value from an expected invalid attempt and route each outcome through the correct loop control.

## Setup

Start with a runnable Cargo binary that reads one line per iteration, parses it as an integer with `expect`, and has a reachable success condition that exits the loop.

## Instructions

1. Record the program's behavior for one valid value and one malformed value before changing it.
2. Replace the parsing `expect` with explicit handling of the returned `Result`.
3. Preserve the parsed integer as the value used by the rest of the successful iteration.
4. Run one sequence containing malformed input followed by valid nonterminal input and then input that reaches the success exit.
5. Record the prompts, branch-specific output, process outcome, and the reason the parse-error branch retries rather than terminates or propagates.

## Success Check

- The baseline evidence shows the malformed value terminated the original program; merely asserting that `expect` can panic does not count.
- In the revised run, malformed input reaches another prompt without a panic, and the later valid values are processed in the same process.
- The success input exits through the program's intended success branch; stopping the run manually after demonstrating retry is the near-miss because it leaves normal completion unproved.
- The explanation distinguishes invalid content from failure to read the input stream and gives a reason for retrying this one.

## Common Failures

- Replacing `expect` with a default value that lets malformed input masquerade as a legitimate number.
- Catching every input and parse failure in one branch even though only invalid content is safe to retry.
- Demonstrating that the loop continues but never proving the normal exit still works.
- Recording a predicted interaction instead of output from one executed process.

## Notes

The sequence makes recovery observable without allowing a restart to fake it: the invalid and valid attempts must occur in one process, and the final success branch must still terminate that process normally.

