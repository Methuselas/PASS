---
object_id: PAT_report_unreal_tool_outcomes_through_a_small_facade
object_type: pattern
name: Report Unreal Tool Outcomes Through a Small Facade
library_path:
- software-engineering
- unreal-engine
- editor
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: PAT_prefer_explicit_error_signaling_for_recoverable_errors
tags:
- unreal_engine
- feedback
- blueprints
- modules
- slate
cross_links: []
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Report Unreal Tool Outcomes Through a Small Facade

## Pattern Rule
**IF** Unreal editor tools need consistent success and failure feedback from C++ and Blueprint
**THEN** provide a small Blueprint-callable facade carrying the operation outcome and useful detail, translate it to the editor's notification API at the presentation boundary, and locate shared code so its callers do not depend on each other.

## Do
- Report successful copy or paste as well as unavailable selection and unsupported targets; identify what the user acted on.
- Prefer unobtrusive notifications for frequent small operations. Use dialogs or persistent UI when the action actually requires them.
- Expose a Blueprint-compatible outcome enum instead of changing the engine just to expose an internal Slate enum.
- Translate the facade's enum to `SNotificationItem` completion states and populate the notification text, subtext and expiration.
- Check that Slate is available and the returned notification handle is valid before updating it; preserve the explicit outcome if presentation is unavailable.
- Use the owning module's export macro for a class called from other modules, and declare dependencies in each consuming module.
- Where game and editor modules both need the same helper, put the genuinely shared interface below both callers rather than creating a plugin/game dependency cycle. Editor-only implementation must remain restricted to editor builds.
- Let unattended or remote callers receive an explicit result and reason even when no Slate notification can be shown.

## Don't
- Don't make an ephemeral success/failure helper pretend to manage pending asynchronous work; pending notifications need a retained handle and later completion.
- Don't fill every gesture with intrusive information the user learns to ignore.
- Don't export a shared class with another module's macro; check the class's actual owning module.

## Checklist
- Can callers distinguish success from failure and learn why a failure occurred?
- Is the feedback visible through the caller's actual interface?
- Can Blueprint call the public facade without depending on internal Slate types?
- Are the module dependency graph and export macro correct?

## Notes
This specializes explicit recoverable-error signaling at an editor-tool presentation boundary. It also separates outcome production from how a person or remote caller sees it. A toast does not replace a machine-readable return, and a shared runtime interface does not make editor-only code appropriate for a packaged game.
