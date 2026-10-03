---
object_id: PAT_pick_the_string_formatting_tool_by_who_writes_the_template
object_type: pattern
name: Pick the String Formatting Tool by Who Writes the Template
library_path:
- software-engineering
- languages
- python
- text
stage_binding: 3 rough
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- strings
- formatting
- f-strings
- templates
cross_links:
- rel: related_to
  target_object_id: PAT_parse_untrusted_text_instead_of_evaluating_it
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Pick the String Formatting Tool by Who Writes the Template

## Pattern Rule
**IF** Python code substitutes values into text
**THEN** choose the tool by where the template comes from: an f-string when the template is written in the code next to the values; `str.format` when the template is written by the program but stored apart from the values; `string.Template` when users or configuration files supply the template; lazy `%`-style arguments when the text goes to `logging`
**ELSE** when existing code already uses `%` or `format` consistently, leave it unless you are changing that line anyway; the forms produce the same strings.

## Do
- Write new inline formatting as f-strings: `f"{name:>10} {total:,.2f} {ratio:.0%}"`. The format spec after the colon is the same mini-language that `format()` and `str.format` use.
- Use `f"{value=}"` while debugging; it prints the expression text and its repr, as in `x=3`.
- Keep a template that must exist before its values (a message table, a translation string) as a plain string and fill it with `template.format(**values)`.
- Use `string.Template('$name').substitute(values)` for templates written by people outside the code; `safe_substitute` leaves unknown placeholders in place instead of raising.
- Pass values to logging calls as arguments, `log.info("loaded %s rows", n)`, so the message is only built if the record is emitted.
- In Python 3.14 and later, use a t-string (`t"..."`) when the text will be processed by something that must escape each value, such as HTML or SQL builders; it yields a `string.templatelib.Template` holding the literal parts and the values separately instead of a finished string.

## Don't
- Don't call `.format` or `%` on a template supplied by a user: replacement fields can read attributes and items of the objects passed in (`"{user.password}"`), so a hostile template can print data you did not mean to expose.
- Don't use string formatting to build SQL or shell commands; use the library's parameter passing.
- Don't format a lone tuple with `%` as `"%s" % t`; a tuple on the right is taken as the argument list. Wrap it, `"%s" % (t,)`, or use an f-string.

## Checklist
- Is the template written in code, stored apart from it, or supplied from outside?
- Could any template here come from a user or a file?
- Are logging calls passing arguments rather than pre-formatted strings?
- Where escaping matters, is it done by the consumer rather than by formatting?

## Notes
Python has accumulated four formatting mechanisms: the printf-style `%` operator, the `str.format` method (with the `format()` built-in and the `__format__` hook it calls), `string.Template`, and f-strings (Python 3.6). All of them build a new string; strings are immutable. f-strings are the usual choice for new code because the values sit inside the text they fill, and since Python 3.12 they accept any expression, including nested quotes of the same kind. The older forms remain fully supported and are still the right tool where the template is not part of the code.
