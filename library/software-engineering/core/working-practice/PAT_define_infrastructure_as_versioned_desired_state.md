---
object_id: PAT_define_infrastructure_as_versioned_desired_state
object_type: pattern
name: Define Infrastructure as Versioned Desired State
library_path:
- software-engineering
- core
- working-practice
stage_binding: 0 design
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- infrastructure_as_code
- deployment
- configuration
- reproducibility
- change_control
cross_links:
- rel: related_to
  target_object_id: PAT_separate_the_durable_need_from_the_current_policy
- rel: related_to
  target_object_id: PAT_give_every_acquired_resource_one_named_owner
reference:
  source_title: Practical Rust Web Projects
  author: Shing Lyu
confidence: medium
references: []
variants: []
---

# Define Infrastructure as Versioned Desired State

## Pattern Rule
**IF** an environment depends on cloud, platform, network, identity, or deployment resources that must be recreated or changed reliably
**THEN** describe the intended state in version-controlled declarations and use a reconciler or deployment tool to converge the environment toward that state, reviewing the proposed create, update, and delete effects before applying them
**ELSE** for genuinely disposable one-off experiments, manual setup can be acceptable when no later environment will depend on reproducing it

## Do
- Keep the durable infrastructure definition beside other reviewed engineering changes so its history, rationale, and rollback path are visible.
- Make environment-specific values explicit inputs rather than hidden console state; keep secrets in an appropriate secret store rather than committing them into the declaration.
- Review destructive replacements, deletions, permission changes, and data-affecting transitions before applying a plan.
- Give deployment tooling authority only over resources and content it is meant to own, and separate deploy-synchronized artifacts from runtime or user-created data when their deletion semantics could overlap.
- Recreate or test the declared environment periodically enough to prove the declaration is not merely documentation of a state that now exists only by accident.

## Don't
- Don't make production configuration depend on an undocumented sequence of console clicks or shell commands that cannot be reviewed or reproduced.
- Don't assume a declarative tool makes every change safe; reconciliation can still replace or delete resources and data.
- Don't hide required configuration in a workstation, personal account, or mutable dashboard value that the declared state does not capture.
- Don't grant the deployment identity broad standing authority merely because it makes initial setup easier when narrower permissions can express the required operations.

## Checklist
- Could another operator recreate the intended environment from the declarations plus documented external inputs?
- Are proposed creates, updates, replacements, deletes, and permission changes visible before application?
- Which resources and data does the deployment tool own, and can its synchronization delete runtime or user-created content?
- Are secrets and environment-specific values supplied without becoming unreviewed hidden state or committed credentials?
- Has the declaration been exercised recently enough to show it still describes reality?

## Notes
The durable benefit of infrastructure as code is not a particular template language. It is turning environment state from a sequence of remembered side effects into reviewable desired state with an explicit reconciliation step. That same step creates a danger: a tool able to make the environment match the declaration may also delete anything it believes should not be there. Ownership boundaries and destructive-change review therefore belong to the pattern rather than being optional deployment-tool details.
