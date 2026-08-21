# Bootstrap a new project

Use this prompt after creating an empty Git repository and adding
`agent-framework` as a submodule.

## Optional: initialize the repository manually

If the repository does not exist yet, initialize it and add the framework
before giving the bootstrap prompt to the agent.

Using a remote framework repository:

```text
git init
git branch -M main
git submodule add <agent-framework-repository-url> agent-framework
git add .gitmodules agent-framework
git commit -m "chore: add agent framework"
```

While developing the framework locally, a local repository path can be used
instead:

```text
git init
git branch -M main
git -c protocol.file.allow=always submodule add ../agent-framework agent-framework
git add .gitmodules agent-framework
git commit -m "chore: add agent framework"
```

The `protocol.file.allow=always` override is included because Git may disable
local-file submodule transport by default. It applies only to that command.
Use a path appropriate for the local checkout layout.

## Prerequisites

- Git repository created and checked out.
- Framework added at exactly `agent-framework/`.
- Docker Desktop or Docker Engine installed and running.
- On Windows, PowerShell is sufficient. Bash, WSL, host Python, and Linux
  verification tools are not required. The agent builds the framework image
  first and runs `python agent-framework/configure.py` inside Docker.
- Have an initial project intent ready. It is recorded verbatim and may be high
  level. Bootstrap does not convert it into product contracts or milestones.

## Prompt

Copy this prompt to the agent and replace the intent placeholder:

> Read `agent-framework/skills/bootstrap-project/SKILL.md` and bootstrap this
> repository according to that skill.
>
> The development host is Windows using PowerShell. Do not rely on Bash, WSL,
> host Python, or Linux development tools being available on the host.
>
> Use Docker as the bootstrap and development environment. Build the
> agent-framework base development image first, then run Linux-only bootstrap
> and development tooling inside Docker. Do not attempt to execute Bash scripts
> directly on the Windows host.
>
> My initial project intent is:
>
> **<describe the project goal here>**
>
> Derive a project name from the repository root or intent. Configure the
> repository with the supplied intent, the default Python version unless I
> specify another supported version, and the minimal executable package/smoke
> test scaffold. Build the project development container and run complete
> framework verification.
>
> Leave contracts, evaluation activities, the roadmap, and milestones empty
> except for their seeded instructional templates. Stop after bootstrap.
>
> At the end, give feedback intended for the author of the bootstrap workflow.
> Point out problems, ambiguities, portability issues, unnecessary work,
> scaffold/toolchain conflicts, and missing framework capabilities you noticed,
> and also state what worked well.

For a non-Windows host, replace the host paragraph with the actual environment
or omit it when no host-specific constraint matters. The Docker-first bootstrap
sequence remains the canonical path.
