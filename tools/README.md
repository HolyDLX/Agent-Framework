# Framework tools

Framework verification tools are discoverable bundles under their native
category directory. Each category has a `category.toml`, `verify_<category>.py`,
and `fix_<category>.py`. Each tool bundle has a `tool.toml` that declares its
Python verify/fix operations and optional default configuration artifacts.

Project assignments live in the machine-managed `[tools.*]` section of
`agent-framework.toml`. Category and tool list order defines execution order.

## Project commands

Bootstrap seeds thin root wrappers, so normal project commands are:

```text
python toolctl.py list
python toolctl.py status
python toolctl.py enable black
python toolctl.py enable black --in-category repository --with-defaults
python toolctl.py disable black
python toolctl.py show-defaults black
python toolctl.py diff-defaults black
python toolctl.py reset-defaults black --force
python toolctl.py fix-duplicates
python run_verification.py
python run_verification.py --fix
```

An unqualified tool name is accepted when globally unique. Canonical stored
identifiers always use `category/tool`. A tool may be assigned to several
categories and will run once per assignment when those categories execute.

## Verification behavior

`run_verification.py` runs categories in configuration order. With `--fix`, all
fix phases run before any verification phase. Individual failures do not stop
later tools. Enabled unavailable tools fail preflight unless
`--ignore-unavailable` is supplied.

Output is concise by default. Complete latest-run logs are written below
`.agent-framework/logs/`, which is ignored by Git. Failures print the final 40
uninterpreted log lines and the complete log location. Use `--verbose` for full
command output.

Category entry points can be called directly for focused work, for example:

```text
python agent-framework/tools/code/verify_code.py
python agent-framework/tools/documentation/fix_documentation.py
```

## Current bundles

- `ci/actionlint`
- `code/black`
- `code/pydoclint`
- `code/pyright`
- `code/ruff`
- `configuration/yamllint`
- `contracts/traceability`
- `documentation/linkcheck`
- `documentation/markdownlint`
- `repository/ai_sanitizer`
- `shell/shellcheck`
- `tests/coverage`
- `tests/pytest`
