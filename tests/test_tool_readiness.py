from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from project_forge_registry.tool_readiness import (
    ToolSpec,
    ToolStatus,
    derive_final_status,
    evaluate_tool,
    evaluate_tools,
    write_report,
)


class ToolReadinessTests(unittest.TestCase):
    def test_evaluate_tool_ready_when_command_found(self) -> None:
        spec = ToolSpec(
            name="Git",
            commands=("git",),
            required=True,
            purpose="test",
            install_hint="install git",
        )

        with patch("project_forge_registry.tool_readiness.shutil.which", return_value="/usr/bin/git"):
            with patch("project_forge_registry.tool_readiness.get_version", return_value="git version test"):
                status = evaluate_tool(spec)

        self.assertTrue(status.available)
        self.assertEqual(status.status, "ready")
        self.assertEqual(status.command_found, "git")
        self.assertEqual(status.version, "git version test")

    def test_evaluate_tool_missing_required(self) -> None:
        spec = ToolSpec(
            name="Git",
            commands=("git",),
            required=True,
            purpose="test",
            install_hint="install git",
        )

        with patch("project_forge_registry.tool_readiness.shutil.which", return_value=None):
            status = evaluate_tool(spec)

        self.assertFalse(status.available)
        self.assertEqual(status.status, "missing_required")

    def test_evaluate_tool_missing_optional(self) -> None:
        spec = ToolSpec(
            name="Obsidian",
            commands=("obsidian",),
            required=False,
            purpose="test",
            install_hint="install obsidian",
        )

        with patch("project_forge_registry.tool_readiness.shutil.which", return_value=None):
            status = evaluate_tool(spec)

        self.assertFalse(status.available)
        self.assertEqual(status.status, "missing_optional")

    def test_derive_final_status_blocked_when_required_missing(self) -> None:
        tools = [
            ToolStatus("Git", True, False, None, None, "purpose", "hint", "missing_required"),
            ToolStatus("Obsidian", False, False, None, None, "purpose", "hint", "missing_optional"),
        ]

        self.assertEqual(derive_final_status(tools), "blocked")

    def test_derive_final_status_ready_with_optional_gaps(self) -> None:
        tools = [
            ToolStatus("Git", True, True, "git", "git version test", "purpose", "hint", "ready"),
            ToolStatus("Obsidian", False, False, None, None, "purpose", "hint", "missing_optional"),
        ]

        self.assertEqual(derive_final_status(tools), "ready_with_optional_gaps")

    def test_derive_final_status_ready_when_all_available(self) -> None:
        tools = [
            ToolStatus("Git", True, True, "git", "git version test", "purpose", "hint", "ready"),
            ToolStatus("Obsidian", False, True, "obsidian", "obsidian test", "purpose", "hint", "ready"),
        ]

        self.assertEqual(derive_final_status(tools), "ready")

    def test_evaluate_tools_accepts_custom_specs(self) -> None:
        specs = [
            ToolSpec("Git", ("git",), True, "purpose", "hint"),
            ToolSpec("Code", ("code",), False, "purpose", "hint"),
        ]

        with patch("project_forge_registry.tool_readiness.shutil.which", return_value=None):
            results = evaluate_tools(specs)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].status, "missing_required")
        self.assertEqual(results[1].status, "missing_optional")

    def test_write_report_contains_safety_statement(self) -> None:
        tools = [
            ToolStatus("Git", True, True, "git", "git version test", "purpose", "hint", "ready"),
            ToolStatus("Obsidian", False, False, None, None, "purpose", "hint", "missing_optional"),
        ]

        with tempfile.TemporaryDirectory() as tmp:
            report_path = Path(tmp) / "tool_readiness_report.md"
            final_status = write_report(report_path, tools, "test-platform")
            text = report_path.read_text(encoding="utf-8")

        self.assertEqual(final_status, "ready_with_optional_gaps")
        self.assertIn("# Project Forge Tool Readiness Report", text)
        self.assertIn("final_status: `ready_with_optional_gaps`", text)
        self.assertIn("- No installs were performed.", text)
        self.assertIn("- No package manager commands were run.", text)
        self.assertIn("Git", text)
        self.assertIn("Obsidian", text)


if __name__ == "__main__":
    unittest.main()
