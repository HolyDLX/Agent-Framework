# Human prompts

This directory contains short, copy-ready prompts for developers who want to
start a framework workflow with an agent.

The files in `human/` are **not authoritative development rules**. They are
human-facing entry points that direct the agent to the corresponding canonical
skill under `skills/` and provide the prerequisites or context the developer
must supply.

| Goal | Human prompt | Canonical agent skill |
| --- | --- | --- |
| Bootstrap a new Python repository | [`bootstrap-project.md`](bootstrap-project.md) | `skills/bootstrap-project/SKILL.md` |
| Implement the current milestone | [`implement-milestone.md`](implement-milestone.md) | `skills/implement-milestone/SKILL.md` |
| Verify an in-progress change | [`verify-change.md`](verify-change.md) | `skills/verify-change/SKILL.md` |
| Write or refine a contract | [`write-contract.md`](write-contract.md) | `skills/write-contract/SKILL.md` |
| Review a completed milestone | [`review-milestone.md`](review-milestone.md) | `skills/review-milestone/SKILL.md` |

Keep these prompts deliberately thin. Workflow details belong in `workflow/`
and `skills/`, so improving the framework does not require developers to learn
or reproduce a long prompt.
