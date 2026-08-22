# M001 implementation notes

- Tool operations remain Python-only and execute as isolated subprocesses.
- A small result-file protocol distinguishes a successful skip from a pass
  without assigning a failing process exit status to direct runner use.
- The `[tools.*]` area of `agent-framework.toml` is machine managed; unrelated
  configuration is preserved byte-for-byte.
- Tool defaults are declared by bundle manifests. Local configuration replaces
  the bundle configuration as a whole.
- Profile inheritance, bundle dependencies, and project-local custom categories
  remain separate planning topics.
