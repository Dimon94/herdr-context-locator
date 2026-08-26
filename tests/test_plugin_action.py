import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
ACTION = ROOT / "scripts" / "copy_context_locator.py"

EXPECTED_PROMPT = """Read the canonical agent-session context for Herdr pane `w27:p1`.

1. Run `herdr agent get w27:p1`.
2. Use `result.agent.agent_session` to locate and search the agent's native session record for information relevant to the current task.
3. Treat pane screen output and scrollback only as diagnostic views, not as the complete conversation.
4. If the pane no longer exists or reports a different session, use the fallback metadata captured below.
5. Keep the source session read-only unless the user explicitly asks you to modify or resume it.

Fallback metadata captured at copy time:
```json
{
  "agent": "pi",
  "pane_id": "w27:p1",
  "session": {
    "kind": "path",
    "source": "herdr:pi",
    "value": "/tmp/source-session.jsonl"
  },
  "working_directory": "/tmp/source-project"
}
```
"""


class PluginActionTests(unittest.TestCase):
    def test_copies_locator_for_focused_agent_session(self):
        result, clipboard, notifications = self._run_fixture(
            self._agent_info(),
            {"HERDR_PANE_ID": "w27:p1"},
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(clipboard, EXPECTED_PROMPT)
        self.assertEqual(
            notifications,
            "notification show copied to clipboard --body w27:p1 · pi\n",
        )

    def test_uses_plugin_context_and_preserves_opaque_session_id(self):
        agent_info = self._agent_info(
            pane_id="w9:p4",
            agent="claude",
            session={
                "agent": "claude",
                "kind": "id",
                "source": "herdr:claude",
                "value": "session-1234",
            },
        )
        result, clipboard, notifications = self._run_fixture(
            agent_info,
            {"HERDR_PLUGIN_CONTEXT_JSON": json.dumps({"focused_pane_id": "w9:p4"})},
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Run `herdr agent get w9:p4`.", clipboard)
        self.assertIn('"kind": "id"', clipboard)
        self.assertIn('"value": "session-1234"', clipboard)
        self.assertEqual(
            notifications,
            "notification show copied to clipboard --body w9:p4 · claude\n",
        )

    def test_rejects_invocation_without_a_focused_pane(self):
        result, clipboard, notifications = self._run_fixture(
            self._agent_info(),
            {},
        )

        self.assertEqual(result.returncode, 1)
        self.assertIsNone(clipboard)
        self.assertEqual(
            notifications,
            "notification show context locator failed --body focus an agent pane and try again\n",
        )

    def test_rejects_agent_without_a_complete_native_session_reference(self):
        agent_info = self._agent_info()
        del agent_info["agent_session"]
        result, clipboard, notifications = self._run_fixture(
            agent_info,
            {"HERDR_PANE_ID": "w27:p1"},
        )

        self.assertEqual(result.returncode, 1)
        self.assertIsNone(clipboard)
        self.assertEqual(
            notifications,
            "notification show context locator failed --body w27:p1 has no complete native session reference; wait for session detection and try again\n",
        )

    def test_rejects_agent_metadata_for_a_different_pane(self):
        result, clipboard, notifications = self._run_fixture(
            self._agent_info(pane_id="w27:p9"),
            {"HERDR_PANE_ID": "w27:p1"},
        )

        self.assertEqual(result.returncode, 1)
        self.assertIsNone(clipboard)
        self.assertEqual(
            notifications,
            "notification show context locator failed --body agent metadata did not match w27:p1; focus the source pane and try again\n",
        )

    def test_rejects_session_owned_by_a_different_agent_kind(self):
        result, clipboard, notifications = self._run_fixture(
            self._agent_info(
                session={
                    "agent": "claude",
                    "kind": "id",
                    "source": "herdr:claude",
                    "value": "session-from-another-agent",
                }
            ),
            {"HERDR_PANE_ID": "w27:p1"},
        )

        self.assertEqual(result.returncode, 1)
        self.assertIsNone(clipboard)
        self.assertEqual(
            notifications,
            "notification show context locator failed --body w27:p1 reported inconsistent agent-session metadata; wait for session detection and try again\n",
        )

    def test_fails_closed_when_no_clipboard_tool_is_available(self):
        result, clipboard, notifications = self._run_fixture(
            self._agent_info(),
            {"HERDR_PANE_ID": "w27:p1"},
            include_clipboard_tool=False,
        )

        self.assertEqual(result.returncode, 1)
        self.assertIsNone(clipboard)
        self.assertEqual(
            notifications,
            "notification show context locator failed --body install pbcopy, wl-copy, xclip, or xsel and try again\n",
        )

    def _agent_info(self, pane_id="w27:p1", agent="pi", session=None):
        if session is None:
            session = {
                "agent": agent,
                "kind": "path",
                "source": f"herdr:{agent}",
                "value": "/tmp/source-session.jsonl",
            }
        return {
            "agent": agent,
            "agent_session": session,
            "cwd": "/tmp/source-project",
            "pane_id": pane_id,
        }

    def _run_fixture(self, agent_info, environment, include_clipboard_tool=True):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bin_dir = root / "bin"
            bin_dir.mkdir()
            clipboard_path = root / "clipboard.txt"
            notifications_path = root / "notifications.txt"
            response_path = root / "agent.json"
            response_path.write_text(
                json.dumps({"result": {"agent": agent_info}}),
                encoding="utf-8",
            )
            self._write_executable(
                bin_dir / "herdr",
                """#!/bin/sh
if [ "$1 $2" = "agent get" ]; then
  /bin/cat "$FAKE_AGENT_RESPONSE"
  exit 0
fi
if [ "$1 $2" = "notification show" ]; then
  printf '%s\n' "$*" >> "$FAKE_NOTIFICATION_LOG"
  exit 0
fi
exit 2
""",
            )
            if include_clipboard_tool:
                self._write_executable(
                    bin_dir / "pbcopy",
                    """#!/bin/sh
/bin/cat > "$FAKE_CLIPBOARD"
""",
                )

            env = os.environ.copy()
            env.pop("HERDR_PANE_ID", None)
            env.pop("HERDR_PLUGIN_CONTEXT_JSON", None)
            env.update(environment)
            env.update(
                {
                    "HERDR_BIN_PATH": str(bin_dir / "herdr"),
                    "PATH": str(bin_dir),
                    "FAKE_AGENT_RESPONSE": str(response_path),
                    "FAKE_CLIPBOARD": str(clipboard_path),
                    "FAKE_NOTIFICATION_LOG": str(notifications_path),
                }
            )
            result = subprocess.run(
                [sys.executable, str(ACTION)],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            clipboard = (
                clipboard_path.read_text(encoding="utf-8")
                if clipboard_path.exists()
                else None
            )
            notifications = (
                notifications_path.read_text(encoding="utf-8")
                if notifications_path.exists()
                else ""
            )
            return result, clipboard, notifications

    def _write_executable(self, path, content):
        path.write_text(content, encoding="utf-8")
        path.chmod(0o755)


if __name__ == "__main__":
    unittest.main()
