"""Project Forge tool readiness checker.

This module checks whether required and recommended local tools are available.
It is intentionally read-only:
- no installs
- no package manager calls
- no remotes
- no push/fetch
- no external project writes
"""

from __future__ import annotations

import argparse
import platform
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


DEFAULT_REPORT_NAME = "tool_readiness_report.md"


@dataclass(frozen=True, slots=True)
class ToolSpec:
    name: str
    commands: tuple[str, ...]
    required: bool
    purpose: str
    install_hint: str


@dataclass(frozen=True, slots=True)
class ToolStatus:
    name: str
    required: bool
    available: bool
    command_found: str | None
    version: str | None
    purpose: str
    install_hint: str
    status: str


@dataclass(frozen=True, slots=True)
class ToolReadinessReport:
    platform_name: str
    tools: list[ToolStatus]
    final_status: str
    report_path: Path


def default_tool_specs() -> list[ToolSpec]:
    return [
        ToolSpec(
            name="Git",
            commands=("git",),
            required=True,
            purpose="Version control and repo status checks.",
            install_hint="Install Git for your platform.",
        ),
        ToolSpec(
            name="Python 3",
            commands=("python3", "python"),
            required=True,
            purpose="Run Project Forge scripts and tests.",
            install_hint="Install Python 3.",
        ),
        ToolSpec(
            name="VS Code / Codium",
            commands=("code", "codium"),
            required=False,
            purpose="Open project folders from the future dashboard.",
            install_hint="Install VS Code or VSCodium.",
        ),
        ToolSpec(
            name="Obsidian",
            commands=("obsidian",),
            required=False,
            purpose="Open and maintain project notes.",
            install_hint="Install Obsidian if you want vault integration.",
        ),
        ToolSpec(
            name="GitHub CLI",
            commands=("gh",),
            required=False,
            purpose="Future GitHub workflow support.",
            install_hint="Install GitHub CLI only if you want CLI GitHub integration.",
        ),
        ToolSpec(
            name="xdg-open",
            commands=("xdg-open",),
            required=False,
            purpose="Open files and links from Linux desktop actions.",
            install_hint="Usually provided by xdg-utils on Linux.",
        ),
        ToolSpec(
            name="desktop-file-validate",
            commands=("desktop-file-validate",),
            required=False,
            purpose="Validate Linux desktop launcher files.",
            install_hint="Usually provided by desktop-file-utils on Linux.",
        ),
        ToolSpec(
            name="PowerShell",
            commands=("pwsh", "powershell"),
            required=False,
            purpose="Windows-oriented future support and scripting.",
            install_hint="Install PowerShell if using Windows workflows.",
        ),
    ]


def detect_platform() -> str:
    return platform.platform()


def find_command(commands: Iterable[str]) -> str | None:
    for command in commands:
        found = shutil.which(command)
        if found:
            return command
    return None


def get_version(command: str | None) -> str | None:
    if not command:
        return None

    candidates = [
        [command, "--version"],
        [command, "-V"],
        [command, "-v"],
    ]

    for candidate in candidates:
        try:
            proc = subprocess.run(
                candidate,
                capture_output=True,
                text=True,
                check=False,
                timeout=5,
            )
        except Exception:
            continue

        output = (proc.stdout or proc.stderr or "").strip().splitlines()
        if proc.returncode == 0 and output:
            return output[0][:180]

    return None


def evaluate_tool(spec: ToolSpec) -> ToolStatus:
    command_found = find_command(spec.commands)
    available = command_found is not None
    version = get_version(command_found)
    if available:
        status = "ready"
    elif spec.required:
        status = "missing_required"
    else:
        status = "missing_optional"

    return ToolStatus(
        name=spec.name,
        required=spec.required,
        available=available,
        command_found=command_found,
        version=version,
        purpose=spec.purpose,
        install_hint=spec.install_hint,
        status=status,
    )


def evaluate_tools(specs: list[ToolSpec] | None = None) -> list[ToolStatus]:
    return [evaluate_tool(spec) for spec in (specs or default_tool_specs())]


def derive_final_status(tools: list[ToolStatus]) -> str:
    if any(tool.required and not tool.available for tool in tools):
        return "blocked"
    if any(not tool.required and not tool.available for tool in tools):
        return "ready_with_optional_gaps"
    return "ready"


def write_report(report_path: Path, tools: list[ToolStatus], platform_name: str) -> str:
    final_status = derive_final_status(tools)
    lines: list[str] = [
        "# Project Forge Tool Readiness Report",
        "",
        f"- platform: `{platform_name}`",
        f"- final_status: `{final_status}`",
        "- mode: `read-only`",
        "",
        "## Summary",
        "",
        f"- required_tools_missing: `{len([t for t in tools if t.required and not t.available])}`",
        f"- optional_tools_missing: `{len([t for t in tools if (not t.required) and not t.available])}`",
        f"- tools_checked: `{len(tools)}`",
        "",
        "## Tool Status",
        "",
        "| Tool | Required | Status | Command | Version |",
        "|---|---:|---|---|---|",
    ]

    for tool in tools:
        required = "yes" if tool.required else "no"
        command = tool.command_found or "not found"
        version = tool.version or "n/a"
        lines.append(
            f"| {tool.name} | {required} | {tool.status} | `{command}` | {version} |"
        )

    lines.extend(["", "## Details", ""])

    for tool in tools:
        lines.extend(
            [
                f"### {tool.name}",
                "",
                f"- required: `{str(tool.required).lower()}`",
                f"- available: `{str(tool.available).lower()}`",
                f"- status: `{tool.status}`",
                f"- command_found: `{tool.command_found or 'not found'}`",
                f"- version: `{tool.version or 'n/a'}`",
                f"- purpose: {tool.purpose}",
                f"- setup_guidance: {tool.install_hint}",
                "",
            ]
        )

    lines.extend(
        [
            "## Safety Statement",
            "",
            "- No installs were performed.",
            "- No package manager commands were run.",
            "- No remotes were added or modified.",
            "- No push/fetch occurred.",
            "- No external project folders were modified.",
            "- This report is advisory only.",
            "",
        ]
    )

    report_path.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(lines)
    report_path.write_text(text, encoding="utf-8")
    return final_status


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="project-forge-check-tools")
    parser.add_argument(
        "--report-name",
        default=DEFAULT_REPORT_NAME,
        help="Report filename under artifacts/.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    report_path = Path("artifacts") / args.report_name
    tools = evaluate_tools()
    platform_name = detect_platform()
    final_status = write_report(report_path, tools, platform_name)

    print("project-forge-check-tools completed")
    print(f"report written: {report_path.resolve()}")
    print(f"final status: {final_status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
