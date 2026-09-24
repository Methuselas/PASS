---
object_id: PAT_place_unreal_k2_compiler_extensions_in_uncooked_modules
object_type: pattern
name: Place Unreal K2 Compiler Extensions in Uncooked Modules
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- k2_nodes
- modules
- packaging
cross_links:
- rel: related_to
  target_object_id: PAT_keep_unreal_editor_dependencies_in_editor_modules
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Place Unreal K2 Compiler Extensions in Uncooked Modules

## Pattern Rule
**IF** a plugin defines `UK2Node` classes or other Blueprint-compiler-only graph extensions that must be available while compiling uncooked content
**THEN** isolate them in an `UncookedOnly` module, keep runtime implementations in a runtime module, and prove the cooked product has no dependency on compiler or editor code.

## Do
- Put custom node classes, action registration, pin reconstruction and Kismet compiler expansion in a module whose descriptor type is `UncookedOnly`.
- Put every function or class referenced by generated runtime bytecode in a runtime-capable module. The compiler module may depend on runtime code; runtime code must not depend back on the compiler module.
- Keep `BlueprintGraph`, `KismetCompiler`, `UnrealEd` and similar compile-time dependencies private to the uncooked module unless an API requirement proves otherwise.
- Give the module a minimal `IModuleInterface` implementation when no startup work is required; node discovery should remain declarative through the Blueprint action database.
- Build editor and uncooked development targets to exercise compilation, then build and inspect a cooked target to verify compiler-only binaries and dependencies are absent.
- Add a dependency-direction test or packaging check so a later convenience include cannot pull uncooked/editor code into runtime modules.

## Don't
- Don't place a K2 compiler node in a runtime module merely because its expanded behavior runs in game.
- Don't place it only in an editor module when uncooked non-editor targets need to compile Blueprints containing the node.
- Don't let runtime objects serialize references to the custom node class after successful compilation.
- Don't infer packaging safety from an editor build alone.

## Checklist
- Are graph/compiler classes isolated from the runtime implementation they expand into?
- Can every target that compiles uncooked Blueprints load the node module?
- Does a cooked build omit compiler/editor modules while retaining the expanded behavior?
- Is dependency direction enforced rather than documented only by convention?

## Notes
`UncookedOnly` describes when compiler tooling is needed, not where the generated behavior executes. Expansion must erase the custom node into runtime-supported bytecode before cooking.
