---
object_id: PAT_scale_agent_effort_to_task_complexity
object_type: pattern
name: Scale Agent Effort to Task Complexity
library_path:
- software-engineering
- ai-systems
- performance
stage_binding: 0 design
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: none
tags:
- ai_agents
- multi_agent
- performance
- resource_budget
- tool_calls
cross_links:
- rel: related_to
  target_object_id: PAT_choose_multi_agent_architecture_for_parallelizable_high_value_work
- rel: related_to
  target_object_id: PAT_budget_agent_context_for_signal_density
- rel: related_to
  target_object_id: PAT_choose_inference_models_by_task_conformance_before_speed
reference:
  source_title: How we built our multi-agent research system
  author: Jeremy Hadfield, Barry Zhang, Kenneth Lien, Florian Scholz, Jeremy Fox, and Daniel Ford
confidence: high
references: []
variants: []
---

# Scale Agent Effort to Task Complexity

## Pattern Rule
**IF** an agent or coordinator can vary the number of workers, tool calls, search breadth, or reasoning effort used for a task
**THEN** classify the task's complexity and apply explicit effort budgets that scale those resources with the expected work
**ELSE** use a fixed small budget only when task size is genuinely uniform and excess exploration cannot become a significant cost or latency problem.

## Do
- Define practical complexity bands such as simple fact lookup, comparison, and complex research, then attach different resource expectations to each band.
- Scale fan-out, tool-call count, and exploration depth together instead of changing only one resource knob.
- Give the coordinator explicit stopping guidance so easy tasks do not keep searching after enough evidence has been found.
- Preserve room to spend more effort when intermediate results reveal that the original complexity estimate was too low.
- Measure whether larger budgets improve task outcomes enough to justify their extra cost and latency.

## Don't
- Don't let every query inherit the maximum subagent count or search depth.
- Don't assume the model will reliably infer an economical effort level without guidance.
- Don't enforce one exact numeric budget across all workloads when task shape and tool costs differ.
- Don't treat more tool calls as progress if the additional work is duplicative or no longer changes the answer.

## Checklist
- What observable properties distinguish simple, comparative, and complex tasks in this product?
- What fan-out and tool-use budget belongs to each class?
- What signals allow the agent to stop early or escalate effort?
- Does the budget include both model tokens and external tool costs?
- Have you measured the marginal quality gain from the larger budget?
- Can a misclassified simple query spiral into unnecessary multi-agent work?

## Notes
When agents misjudge how much work a query deserves, explicit effort-scaling rules may improve efficiency. Calibrate worker counts, tool budgets, and search depth from measured task outcomes; numeric thresholds from one workload are not universal. The transferable pattern is to make resource allocation an explicit function of task complexity and measured value rather than an unconstrained emergent behavior.
