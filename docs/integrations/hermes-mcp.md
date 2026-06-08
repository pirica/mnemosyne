# Mnemosyne + Hermes Agent

Mnemosyne is the native memory provider for Hermes Agent. Two integration paths:

## Path 1: MCP

Add to your Hermes `config.yaml`:

```yaml
mcp:
  servers:
    mnemosyne:
      command: mnemosyne
      args: ["mcp"]
```

Tools register as native Hermes commands.

## Path 2: Hermes Plugin (recommended)

**Do NOT install inside Hermes' managed venv** — `hermes update` rebuilds the
venv and wipes extra packages. Use pipx or a dedicated virtualenv.

```bash
# Stable, survives Hermes updates
pipx install mnemosyne-hermes
hermes config set memory.provider mnemosyne
hermes gateway restart
```

For speed with pipx:

```bash
export PIPX_DEFAULT_BACKEND=uv
pipx install mnemosyne-hermes
```

### Disable legacy memory

When Mnemosyne is active, disable Hermes' built-in memory to avoid duplication
and token waste:

```bash
hermes tools disable memory
```

Also add to `~/.hermes/config.yaml`:

```yaml
memory:
  enabled: false
  user_profile_enabled: false
```

Both the CLI disable and the config keys are needed — the CLI handles runtime,
the config handles startup.

### Upgrade

```bash
pipx upgrade mnemosyne-hermes
hermes gateway restart
```

### Standalone venv (fallback)

```bash
python3 -m venv ~/.hermes/mnemosyne-venv
~/.hermes/mnemosyne-venv/bin/pip install mnemosyne-hermes
~/.hermes/mnemosyne-venv/bin/mnemosyne-hermes install --force
hermes config set memory.provider mnemosyne
hermes gateway restart
```

## Usage

In Hermes, use the built-in commands:
- `mnemosyne_remember` — Store a memory
- `mnemosyne_recall` — Search memories
- `mnemosyne_forget` — Remove a memory
- `mnemosyne_stats` — View memory statistics
- `mnemosyne_sleep` — Run consolidation
