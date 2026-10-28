---
object_id: PAT_pass_rust_child_arguments_as_argv_unless_shell_syntax_is_the_contract
object_type: pattern
name: Pass Rust Child Arguments as argv Unless Shell Syntax Is the Contract
library_path:
- software-engineering
- languages
- rust
- processes
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- rust
- processes
- command
- argv
- shell
- parsing
- security
cross_links:
- rel: related_to
  target_object_id: AP_launch_and_supervise_a_rust_child_process
- rel: related_to
  target_object_id: PAT_choose_rust_child_process_api_by_completion_contract
- rel: related_to
  target_object_id: PAT_separate_parsing_stages_by_representation_boundary
reference:
  source_title: Practical System Programming for Rust Developers
  author: Prabhu Eshwarla
confidence: medium
references: []
variants: []
---

# Pass Rust Child Arguments as argv Unless Shell Syntax Is the Contract

## Pattern Rule
**IF** a Rust program must launch an external program from structured values or from user-entered command text
**THEN** keep the program and each argument as distinct structured argument values for direct Command execution, and introduce an explicit shell parser or deliberately selected shell only when shell-language semantics are part of the contract
**ELSE** do not add shell interpretation when the caller already has a structured executable and argument list

## Do
- Pass one logical argument per Command::arg/args item. Preserve OS-native argument values when the surrounding contract does not require Unicode text.
- Define a grammar before accepting quoting, escaping, pipelines, redirection, globbing, variable expansion, command substitution, or other shell operators from text input.
- If the product intentionally delegates to a shell, select that shell explicitly and treat its language, platform differences, quoting rules, and injection surface as part of the public boundary.
- Keep parsing separate from process launch so invalid syntax is rejected before any child is spawned and the resulting executable/argument structure can be tested directly.
- Test at least an argument containing whitespace, quotes/escape characters, an operator-looking token such as | or >, and platform-specific executable/argument cases that the supported targets permit.

## Don't
- Don't concatenate a command line into Command::new; that parameter names the program, not a shell command string.
- Don't use split_whitespace as a shell parser once whitespace can occur inside a quoted/escaped argument or operators carry syntax.
- Don't expect Command::arg/args to perform shell quoting removal, word splitting, glob expansion, variable substitution, pipelines, or redirection.
- Don't introduce sh -c, cmd /C, batch-file execution, or another command interpreter around untrusted text merely to make shell syntax convenient; doing so changes the security and portability contract.

## Checklist
- Is the input already an executable plus structured arguments, or is it intentionally a shell language?
- Which component owns tokenization, quoting/escaping, operators, and expansion semantics?
- Can user-controlled text reach a shell interpreter, batch-file parser, or other nonstandard argument decoder?
- Are program-not-found, parse failure, and child nonzero exit represented as different outcomes?
- Do tests prove that whitespace and operator-looking characters are preserved or interpreted according to the declared contract?

## Notes
Rust Command is a structured process launcher, not a shell parser. On Unix, the program and arguments map naturally to an argv-style process boundary. On Windows, Rust encodes the structured arguments for the target process, and some interpreters use nonstandard decoding. In either case, shell syntax appears only if the application explicitly parses it or launches a shell/interpreter that does.

This distinction is also a security boundary. Direct structured argument passing avoids accidental shell interpretation, while deliberately invoking a shell transfers correctness and injection risk to that shell language. Windows command decoders such as cmd.exe and batch files have additional argument-handling caveats, so platform-specific interpreters should remain explicit rather than hidden behind a generic command string.
