from __future__ import annotations

from pathlib import Path

from .remote_models import RemotePlan, RemoteVerify


def write_remote_plan_report(path: Path, plan: RemotePlan) -> None:
    lines = [
        "# Remote Plan Report",
        "",
        "## Scope",
        "",
        f"- Mode: `{plan.mode}`",
        f"- Slug: `{plan.slug}`",
        f"- Passport dir: `{plan.passport_dir}`",
        f"- Passport file: `{plan.record.passport_path}`",
        f"- Local path: `{plan.record.local_path}`",
        "",
        "## Policy Defaults",
        "",
        f"- GitHub remote name: `{plan.defaults.github_remote_name}`",
        f"- Codeberg remote name: `{plan.defaults.codeberg_remote_name}`",
        f"- GitHub visibility: `{plan.defaults.github_visibility}`",
        f"- Codeberg visibility: `{plan.defaults.codeberg_visibility}`",
        f"- Default branch: `{plan.defaults.default_branch}`",
        f"- Push behavior: `{plan.defaults.push_behavior}`",
        "",
        "## Eligibility",
        "",
        f"- Eligible: {str(plan.eligible).lower()}",
        f"- Policy status: `{plan.policy_status}`",
        "",
        "## Notes",
        "",
    ]
    if not plan.reasons:
        lines.append("- none")
    else:
        for reason in plan.reasons:
            lines.append(f"- {reason}")

    lines.extend(
        [
            "",
            "## Safety Confirmation",
            "",
            "- Read-only planning mode: yes",
            "- Remote add/modify actions performed: no",
            "- Push/fetch performed: no",
            "- Secret scan implementation: pending Phase 7b/8",
            "- Push-ready determination in this phase: no",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_remote_verify_report(path: Path, verify: RemoteVerify) -> None:
    lines = [
        "# Remote Verify Report",
        "",
        "## Scope",
        "",
        f"- Mode: `{verify.mode}`",
        f"- Slug: `{verify.slug}`",
        f"- Passport dir: `{verify.passport_dir}`",
        f"- Passport file: `{verify.record.passport_path}`",
        f"- Local path: `{verify.record.local_path}`",
        "",
        "## Policy Defaults",
        "",
        f"- GitHub remote name: `{verify.defaults.github_remote_name}`",
        f"- Codeberg remote name: `{verify.defaults.codeberg_remote_name}`",
        f"- GitHub visibility: `{verify.defaults.github_visibility}`",
        f"- Codeberg visibility: `{verify.defaults.codeberg_visibility}`",
        f"- Default branch policy: `{verify.defaults.default_branch}`",
        "",
        "## Eligibility",
        "",
        f"- Eligible: {str(verify.eligible).lower()}",
        f"- Policy status: `{verify.policy_status}`",
    ]
    if verify.reasons:
        lines.extend(["", "## Eligibility Notes", ""])
        for reason in verify.reasons:
            lines.append(f"- {reason}")

    lines.extend(["", "## Local Git State", ""])
    lines.append(f"- Inside git repo: {str(verify.remote_state.inside_git_repo).lower()}")
    lines.append(
        f"- Current branch: `{verify.remote_state.current_branch if verify.remote_state.current_branch else 'unknown'}`"
    )
    lines.append(
        f"- Working tree clean (if checked): "
        f"`{verify.remote_state.clean_working_tree if verify.remote_state.clean_working_tree is not None else 'not_checked'}`"
    )
    if verify.remote_state.clean_working_tree_lines:
        lines.append("- Working tree details:")
        for row in verify.remote_state.clean_working_tree_lines:
            lines.append(f"  - `{row}`")

    lines.extend(["", "## Remote Snapshot", ""])
    if not verify.remote_state.remotes:
        lines.append("- No configured remotes detected.")
    else:
        for name, url, direction in verify.remote_state.remotes:
            lines.append(f"- `{name}` `{direction}` -> `{url}`")

    lines.extend(["", "## Verification Checks", ""])
    for check in verify.checks:
        lines.append(
            f"- `{check.name}` required={str(check.required).lower()} "
            f"passed={str(check.passed).lower()} detail={check.detail}"
        )

    lines.extend(
        [
            "",
            "## Safety Confirmation",
            "",
            "- Read-only verification mode: yes",
            "- Remote add/modify actions performed: no",
            "- Push/fetch performed: no",
            "- Secret scan implementation: pending Phase 7b/8",
            "- Push-ready determination in this phase: no",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
