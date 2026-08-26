# Herdr Context Locator

A small [Herdr](https://herdr.dev) plugin that copies a self-describing locator for the focused coding agent's canonical session context.

The locator contains the live Herdr pane ID plus a snapshot of the native agent-session reference. Paste it into another coding-agent session so that agent can find and search the source agent's native conversation record.

## What it copies

- The focused Herdr pane ID.
- The detected agent kind.
- The native session reference reported by Herdr.
- The source working directory.
- Instructions to prefer the agent's native session record over terminal scrollback.

It does **not** copy the conversation, terminal output, repository contents, or credentials. It does not resume or modify the source session.

## Requirements

- Herdr 0.8.2 or newer.
- Python 3.
- macOS with `pbcopy`, or Linux with `wl-copy`, `xclip`, or `xsel`.
- A focused Herdr pane containing a detected agent with `agent_session` metadata.

## Install

```bash
herdr plugin install Dimon94/herdr-context-locator
```

Add the keybinding to `~/.config/herdr/config.toml`:

```toml
[[keys.command]]
key = "prefix+y"
type = "plugin_action"
command = "dimon.context-locator.copy-focused-context"
description = "copy focused agent context locator"
```

Reload Herdr:

```bash
herdr server reload-config
```

Focus the source agent pane, press the Herdr prefix, release it, then press `Y`. Paste the copied locator into the receiving agent session.

## Failure behavior

The action validates the focused pane, detected agent, and native session reference before invoking a clipboard command. It reports success only after that command exits successfully. Herdr shows a recovery-oriented notification when any required input is unavailable.

## Privacy and limits

The locator may contain a local filesystem path or an opaque native session ID. It is copied only to the host clipboard and sent nowhere by this plugin. The receiving agent can read the context only while the referenced native session record still exists and is accessible to it.

Pane screen output and scrollback are diagnostic views, not the canonical conversation. The plugin stores no transcript and owns no persistent state.

## Development

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile scripts/copy_context_locator.py
herdr plugin link "$PWD"
```

The product boundary and acceptance criteria live in [`docs/product/mvp.md`](docs/product/mvp.md).

## License

MIT
