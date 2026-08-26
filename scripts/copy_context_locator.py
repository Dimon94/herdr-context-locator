#!/usr/bin/env python3
"""Herdr plugin action that copies a canonical agent-session locator.

COORD: repo://scripts/copy_context_locator.py
INPUT: Herdr invocation environment and `herdr agent get` JSON.
OUTPUT: One locator prompt in the host clipboard and a Herdr notification.
POS: Owns locator validation and rendering; owns no session data or transcript.
TEST: repo://tests/test_plugin_action.py
PROTOCOL: Keep the clipboard contract and manifest action synchronized.
"""

from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import sys
from typing import NoReturn


class ActionError(Exception):
    """A stable, user-recoverable plugin action failure."""


HERDR = os.environ.get("HERDR_BIN_PATH", "herdr")


def notify(title: str, body: str) -> None:
    try:
        subprocess.run(
            [HERDR, "notification", "show", title, "--body", body],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        pass


def fail(message: str) -> NoReturn:
    raise ActionError(message)


def focused_pane_id() -> str:
    pane_id = os.environ.get("HERDR_PANE_ID", "").strip()
    if pane_id:
        return pane_id

    encoded_context = os.environ.get("HERDR_PLUGIN_CONTEXT_JSON", "")
    if encoded_context:
        try:
            context = json.loads(encoded_context)
        except json.JSONDecodeError:
            context = {}
        pane_id = context.get("focused_pane_id", "")
        if isinstance(pane_id, str) and pane_id.strip():
            return pane_id.strip()

    fail("focus an agent pane and try again")


def read_agent(pane_id: str) -> dict[str, object]:
    try:
        result = subprocess.run(
            [HERDR, "agent", "get", pane_id],
            capture_output=True,
            text=True,
            check=True,
        )
        response = json.loads(result.stdout)
        agent = response["result"]["agent"]
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError, KeyError, TypeError):
        fail(f"could not read agent metadata for {pane_id}; confirm the agent is still running")

    if not isinstance(agent, dict):
        fail(f"could not read agent metadata for {pane_id}; confirm the agent is still running")
    return agent


def required_text(mapping: dict[str, object], key: str, failure: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        fail(failure)
    return value.strip()


def fallback_metadata(pane_id: str, agent_info: dict[str, object]) -> dict[str, object]:
    reported_pane_id = required_text(
        agent_info,
        "pane_id",
        f"agent metadata did not match {pane_id}; focus the source pane and try again",
    )
    if reported_pane_id != pane_id:
        fail(f"agent metadata did not match {pane_id}; focus the source pane and try again")

    failure = f"{pane_id} has no complete native session reference; wait for session detection and try again"
    agent_kind = required_text(agent_info, "agent", failure)
    working_directory = required_text(agent_info, "cwd", failure)
    session = agent_info.get("agent_session")
    if not isinstance(session, dict):
        fail(failure)
    session_agent_kind = required_text(session, "agent", failure)
    if session_agent_kind != agent_kind:
        fail(
            f"{pane_id} reported inconsistent agent-session metadata; "
            "wait for session detection and try again"
        )

    return {
        "agent": agent_kind,
        "pane_id": pane_id,
        "session": {
            "kind": required_text(session, "kind", failure),
            "source": required_text(session, "source", failure),
            "value": required_text(session, "value", failure),
        },
        "working_directory": working_directory,
    }


def render_locator(metadata: dict[str, object]) -> str:
    pane_id = str(metadata["pane_id"])
    pane_argument = shlex.quote(pane_id)
    encoded_metadata = json.dumps(metadata, ensure_ascii=False, indent=2)
    return f"""Read the canonical agent-session context for Herdr pane `{pane_id}`.

1. Run `herdr agent get {pane_argument}`.
2. Use `result.agent.agent_session` to locate and search the agent's native session record for information relevant to the current task.
3. Treat pane screen output and scrollback only as diagnostic views, not as the complete conversation.
4. If the pane no longer exists or reports a different session, use the fallback metadata captured below.
5. Keep the source session read-only unless the user explicitly asks you to modify or resume it.

Fallback metadata captured at copy time:
```json
{encoded_metadata}
```
"""


def clipboard_command() -> list[str]:
    candidates = (
        ("pbcopy", []),
        ("wl-copy", []),
        ("xclip", ["-selection", "clipboard"]),
        ("xsel", ["--clipboard", "--input"]),
    )
    for executable, arguments in candidates:
        path = shutil.which(executable)
        if path:
            return [path, *arguments]
    fail("install pbcopy, wl-copy, xclip, or xsel and try again")


def copy_to_clipboard(content: str) -> None:
    try:
        subprocess.run(
            clipboard_command(),
            input=content,
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        fail("the clipboard command failed; verify the local clipboard tool and try again")


def main() -> int:
    try:
        pane_id = focused_pane_id()
        metadata = fallback_metadata(pane_id, read_agent(pane_id))
        copy_to_clipboard(render_locator(metadata))
    except ActionError as error:
        notify("context locator failed", str(error))
        print(str(error), file=sys.stderr)
        return 1

    notify("copied to clipboard", f"{pane_id} · {metadata['agent']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
