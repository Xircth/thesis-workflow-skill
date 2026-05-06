# Metaso MCP Setup

Use this reference only when academic search or literature supplementation is needed.

## Safety Rules

- Never put the user's Metaso API key in this skill, sample text, logs, screenshots, or committed files.
- Ask the user to obtain a key from `https://metaso.cn/search-api/api-keys`.
- After receiving the key, identify the active agent and its local config mechanism before writing anything.
- Before modifying a config file, state the target file path and ask for explicit confirmation if the operation changes a global/shared config.
- Redact the key in all output, for example `meta_sk_****abcd`.
- Prefer environment variables or local secret storage when the active agent supports it.

## Configuration Flow

1. Detect active environment: Codex, OpenCode, Claude Code, or other.
2. Inspect existing MCP configuration files in user config directories and workspace config files.
3. If a `metaso` server already exists, validate it without changing the key.
4. If missing, ask the user for the API key and configure a `metaso` MCP entry according to the active agent's existing config format.
5. Restart or reload the agent/MCP service if required by the active environment.
6. Run a harmless test query and report only whether it works.

## Literature Search Output

For each candidate source, record:

- title
- authors
- year
- venue or publisher
- DOI or formal URL when available
- why it is relevant
- suggested thesis section
- verification status

Never treat MCP output as final bibliography without verification.
