---
object_id: PAT_apply_data_governance_to_external_evaluation_providers
object_type: pattern
name: Apply Data Governance to External Evaluation Providers
library_path:
- software-engineering
- ai-systems
- security
stage_binding: 4 final
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: none
tags:
- ai_agents
- evaluation
- security
- privacy
- data_retention
- third_party
cross_links:
- rel: related_to
  target_object_id: PAT_enforce_agent_policies_in_deterministic_middleware
- rel: related_to
  target_object_id: PAT_scope_agent_state_and_authority_per_tenant
reference:
  source_title: Jev is now available in LangSmith Evals
  author: Winston Huynh
confidence: high
references: []
variants: []
---

# Apply Data Governance to External Evaluation Providers

## Pattern Rule
**IF** an external evaluator will receive production traces, messages, prompts, outputs, thread state, or other agent context
**THEN** treat that evaluator as a production data processor and verify retention, privacy, tenancy, and disclosure requirements before sending the data
**ELSE** keep evaluation local or limit the state to data that is explicitly safe for the provider to receive.

## Do
- Inventory exactly which run, thread, message, prompt, output, and metadata fields the evaluator state will contain.
- Verify the provider's current retention and privacy behavior for the specific product path, account tier, and agreement you will actually use.
- Remove secrets and data that are unnecessary for the grading criterion before the evaluator request leaves your trust boundary.
- Apply tenant scoping before evaluation so one customer's trace cannot be mixed into another customer's evaluation context or feedback stream.
- Enforce redaction and disclosure rules in deterministic middleware or preprocessing rather than asking the judge to ignore sensitive fields after receiving them.
- Record which external provider produced each feedback signal so audits can reconstruct where production data was sent.
- Recheck provider terms and retention behavior when integrations, account tiers, contracts, or data flows change.

## Don't
- Don't assume observability or evaluation traffic is harmless telemetry; traces can contain the same sensitive content as the production interaction itself.
- Don't send an entire trace when the criterion only needs a narrow subset of fields.
- Don't rely on a prompt instruction such as "ignore PII" as a substitute for removing data the provider should not receive.
- Don't infer zero-retention or equivalent protections from the evaluator's speed, price, or model architecture.
- Don't let a new evaluator integration bypass the same privacy review applied to model and tool providers.

## Checklist
- What exact production data reaches the evaluator?
- Does the provider retain prompts, outputs, traces, or derived feedback under the path being used?
- Can the criterion be evaluated from a smaller or redacted state?
- Are tenant boundaries preserved before and after evaluation?
- Are provider identity and evaluator version observable in audit records?
- Is retention/privacy behavior revalidated after material integration or contract changes?

## Notes
Online evaluation often replays some of the richest data in an agent system: full traces, user messages, tool outputs, and thread context. Adding a judge therefore changes the data-flow graph even when the judge is used only for observability.

Evaluation prompts and outputs sent through an external provider may be retained. Provider terms can change; the durable lesson is to verify the actual retention contract before enabling an external evaluator on production traces.
