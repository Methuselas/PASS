---
object_id: PAT_keep_your_names_off_builtins_and_importable_modules
object_type: pattern
name: Keep Your Names Off Built-ins and Importable Modules
library_path:
- software-engineering
- languages
- python
- naming
stage_binding: 3 rough
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- naming
- builtins
- imports
- shadowing
cross_links:
- rel: related_to
  target_object_id: PAT_use_descriptive_names
reference:
  source_title: 'Beyond the Basic Stuff with Python: Best Practices for Writing Clean Code'
  author: Al Sweigart
confidence: high
references: []
variants: []
---

# Keep Your Names Off Built-ins and Importable Modules

## Pattern Rule
**IF** you are choosing a bare name that will be bound at module, function or class-body level, or a filename for a Python module or package
**THEN** choose one that no built-in and no importable module already answers to, because Python lets your binding silently replace theirs and the failure surfaces later, elsewhere, naming the victim instead of the cause.

## Do
- Check the candidate against the running interpreter before you commit to it: `hasattr(builtins, name)` for a built-in, `name in sys.stdlib_module_names` for a standard-library module, and `importlib.util.find_spec(name)` for anything installed — run that last one before the file exists, or it finds your own file.
- Treat a `.py` filename as a name in every importer's namespace. The directory of the script being run, or the current directory under `python -c`, is searched before the standard library and installed packages, so a helper saved as `random.py` is what every `import random` in the process receives — including imports made inside the standard library. With one beside the script, `import tempfile` fails with `ImportError: cannot import name 'Random' from 'random'`.
- Qualify a bare name that genuinely means an id or a type: `user_id`, `record_type`, `kind`. Attribute access shadows nothing — `self.id` and `row.type` leave `id()` and `type()` intact — so the collision lives in bare names, not dotted ones.
- Treat a field in a class body, including a `dataclass` field, as a bare name in class scope. A field `list: int = 0` followed by `tags: list[str]` in the same class is created without complaint on 3.14, because annotations are evaluated lazily, and then raises `TypeError: 'int' object is not subscriptable` when anything reads the annotations — `typing.get_type_hints`, `annotationlib.get_annotations`, or a serializer built on them.
- Use `python -P` to confirm a suspected module collision: it stops the script's directory from being searched first, so a failure that disappears under `-P` is a local file standing in for a real module. Then rename the file; the flag fixes one invocation, not the project.

## Don't
- Don't work from a memorised list of names to avoid. Such lists mix three hazards: built-ins such as `id`, `input`, `hash` and `format` are dangerous as variables; standard-library modules such as `random`, `email`, `queue` and `types` are dangerous as filenames; and names such as `file` and `date` are neither in current Python. Ask the interpreter.
- Don't rely on the error message to name the collision. A file shadowing a standard-library module gets a hint (`consider renaming '…random.py' since it has the same name as the standard library module`), but a file shadowing an installed package can produce only `AttributeError: module 'pip' has no attribute 'main'`.
- Don't rebind a built-in at module scope on the grounds that this module does not need it. Everything later in the module, including code someone adds next year, gets your value: after `list = ['cat']`, `list(range(5))` raises `TypeError: 'list' object is not callable`.

## Checklist
- Does any new bare name at module, function or class-body level appear in `dir(builtins)`?
- Does any new `.py` file or package directory name appear in `sys.stdlib_module_names` or resolve through `importlib.util.find_spec` to something installed?
- If an import reports "has no attribute" or "cannot import name" for something that certainly exists, does the failure go away under `python -P`?

## Notes
Both collisions are legal, silent when the binding is made, and fail at a distance. A bare name resolves through local, enclosing, module and finally built-in scope, so any binding at an inner level wins; imports search the running script's directory before anything installed. The traceback then names what was displaced — `list`, `Random`, `tempfile` — rather than the file or assignment that displaced it.

Scope sets how far the damage reaches. A parameter named `id` shadows the built-in only inside its function, and the built-in is intact once the call returns. A module-level rebinding reaches the rest of that module. A module file reaches every importer in the process, the standard library included, which is why the filename case is the one that breaks code nobody on the project wrote.

Error messages quoted here are from CPython 3.14.7, identical on the default and free-threaded builds.
