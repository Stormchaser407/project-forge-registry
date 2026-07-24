#!/usr/bin/env python3
"""One-shot migration for retiring Project Forge's Cerberus name vetoes."""

from __future__ import annotations

import re
from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(
            f"{path}: expected one match, found {count}: {old!r}"
        )
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


def replace_method(path: str, method: str, replacement: str) -> None:
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    pattern = rf"\n    def {re.escape(method)}\(.*?(?=\n    def |\n\nif __name__)"
    updated, count = re.subn(
        pattern,
        "\n" + replacement.rstrip(),
        text,
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise SystemExit(f"{path}: method {method} match count {count}")
    target.write_text(updated, encoding="utf-8")


def migrate_source() -> None:
    replace_once(
        "src/project_forge_registry/obsidian_mirror_generation.py",
        '    if record.slug == "cerberus" or "cerberus" in record.slug or "cerberus" in record.local_path.lower():\n'
        '        reasons.append("cerberus_protected")\n',
        "",
    )
    replace_once(
        "src/project_forge_registry/export_sync.py",
        "    slug_lower = record.slug.lower()\n"
        "    local_path_lower = record.local_path.lower()\n\n",
        "",
    )
    replace_once(
        "src/project_forge_registry/export_sync.py",
        '    if slug_lower == "cerberus" or "cerberus" in slug_lower or "cerberus" in local_path_lower:\n'
        '        reasons.append("cerberus_protected")\n',
        "",
    )
    replace_once(
        "src/project_forge_registry/remote_policy.py",
        "    slug_lower = record.slug.lower()\n"
        "    local_lower = str(record.local_path).lower()\n\n",
        "",
    )
    replace_once(
        "src/project_forge_registry/remote_policy.py",
        '    if slug_lower == "cerberus" or "cerberus" in slug_lower or "cerberus" in local_lower:\n'
        '        reasons.append("cerberus_protected")\n',
        "",
    )
    replace_once(
        "src/project_forge_registry/remote_policy.py",
        '        or item == "cerberus_protected"\n',
        "",
    )
    replace_once(
        "src/project_forge_registry/project_sync.py",
        "    slug_lower = slug.lower()\n"
        '    if slug_lower == "cerberus" or "cerberus" in slug_lower:\n'
        '        reasons.append("cerberus_protected")\n\n',
        "",
    )
    replace_once(
        "src/project_forge_registry/project_sync.py",
        '        local_path = str(project.get("local_path", "")).lower()\n',
        "",
    )
    replace_once(
        "src/project_forge_registry/project_sync.py",
        '        if "cerberus" in local_path:\n'
        '            reasons.append("cerberus_protected")\n',
        "",
    )
    replace_once(
        "src/project_forge_registry/workspace_generation.py",
        '    if "cerberus_special_case_candidate" in record.safety_warnings:\n'
        '        reasons.append("safety_warning=cerberus_special_case_candidate")\n',
        "",
    )

    replace_once(
        "src/project_forge_registry/dashboard_inventory.py",
        "from typing import Any\n\n",
        "from typing import Any\n\n"
        "from .category_policy import normalize_repo_category\n\n",
    )
    replace_once(
        "src/project_forge_registry/dashboard_inventory.py",
        '''        for row in reader:
            rows.append(
                RepoDiscoveryRow(
                    slug=row["slug"],
                    path=Path(row["path"]),
                    git_status=row["git_status"],
                    has_readme=parse_bool(row["has_readme"]),
                    has_agents=parse_bool(row["has_agents"]),
                    has_code_workspace=parse_bool(row["has_code_workspace"]),
                    has_project_forge_marker=parse_bool(
                        row["has_project_forge_marker"]
                    ),
                    remote_count=int(row["remote_count"]),
                    category=row["category"],
                )
            )
''',
        '''        for row in reader:
            git_status = row["git_status"]
            marker = parse_bool(row["has_project_forge_marker"])
            category = normalize_repo_category(row["category"], git_status, marker)
            rows.append(
                RepoDiscoveryRow(
                    slug=row["slug"],
                    path=Path(row["path"]),
                    git_status=git_status,
                    has_readme=parse_bool(row["has_readme"]),
                    has_agents=parse_bool(row["has_agents"]),
                    has_code_workspace=parse_bool(row["has_code_workspace"]),
                    has_project_forge_marker=marker,
                    remote_count=int(row["remote_count"]),
                    category=category,
                )
            )
''',
    )


def migrate_tests() -> None:
    replace_method(
        "tests/test_obsidian_mirror_generation.py",
        "test_cerberus_related_records_are_protected",
        '''    def test_cerberus_related_records_are_eligible(self) -> None:
        plan = self.make_plan([self.make_record("cerberus_helper")])

        self.assertEqual(
            {entry.record.slug for entry in plan.eligible_entries},
            {"cerberus_helper"},
        )''',
    )
    replace_method(
        "tests/test_export_sync.py",
        "test_cerberus_slug_is_protected",
        '''    def test_cerberus_slug_is_eligible(self) -> None:
        artifacts_root = repository_artifacts_root()
        with tempfile.TemporaryDirectory(dir=artifacts_root) as artifacts_tmp, tempfile.TemporaryDirectory() as vault_tmp, tempfile.TemporaryDirectory() as project_tmp:
            artifacts_dir = Path(artifacts_tmp)
            passport_dir = artifacts_dir / "project_passports"
            vault_root = Path(vault_tmp)
            export_docs_dir = vault_root / "cerberus" / "_export" / "docs"
            passport_dir.mkdir(parents=True)
            export_docs_dir.mkdir(parents=True)
            (export_docs_dir / "guide.md").write_text("# Guide" + chr(10), encoding="utf-8")
            write_passport(
                passport_dir / "cerberus.project.yml",
                slug="cerberus",
                local_path=project_tmp,
            )
            plan = build_sync_plan(
                mode="dry-run",
                slug="cerberus",
                passport_dir=passport_dir,
                vault_project_root=vault_root,
                repo_root_override=None,
                include_files=set(),
                exclude_files=set(),
                report_name="export_sync_report.md",
                backup_suffix="stamp",
            )
            self.assertTrue(plan.entry.eligible)
            self.assertEqual(plan.entry.reasons, [])
            self.assertEqual(plan.files_planned, 1)''',
    )
    replace_method(
        "tests/test_remote_policy.py",
        "test_plan_blocks_cerberus",
        '''    def test_plan_treats_cerberus_normally(self) -> None:
        with self.temp_in_repo() as tmp:
            artifacts = Path(tmp)
            passport_dir = artifacts / "project_passports"
            passport_dir.mkdir()
            write_passport(
                passport_dir / "cerberus.project.yml",
                slug="cerberus",
                local_path=str(artifacts),
            )
            parser = build_parser()
            args = parser.parse_args(
                ["plan", "--slug", "cerberus", "--passport-dir", str(passport_dir)]
            )
            plan = build_plan(args)
            self.assertTrue(plan.eligible)
            self.assertEqual(plan.policy_status, "needs_approval")
            self.assertNotIn("cerberus_protected", plan.reasons)''',
    )
    replace_method(
        "tests/test_project_sync.py",
        "test_detect_protected_project_from_slug_and_passport",
        '''    def test_detect_protected_project_uses_explicit_policy_only(self) -> None:
        with tempfile.TemporaryDirectory(dir=repository_root() / "artifacts") as artifacts_tmp:
            passport_dir = Path(artifacts_tmp) / "project_passports"
            passport_dir.mkdir(parents=True)
            passport_path = passport_dir / "cerberus.project.yml"
            passport_path.write_text(
                "\n".join(
                    [
                        "project:",
                        "  slug: cerberus",
                        '  name: "Cerberus"',
                        "  category: active_project",
                        "  status: review",
                        "  registry_action: register_full",
                        '  local_path: "/home/cole/cerberus"',
                        "safety:",
                        "  warnings: []",
                        "  do_not_sync: false",
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            reasons = detect_protected_project(passport_path, "cerberus")
            self.assertEqual(reasons, [])''',
    )

    path = Path("tests/test_dashboard_inventory.py")
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        'self.assertEqual(derive_risk_light(rows["protected"]), "red")',
        'self.assertEqual(derive_risk_light(rows["protected"]), "green")',
    )
    text = text.replace(
        '''        self.assertEqual(
            derive_recommended_action(rows["protected"]),
            "protected_manual_review",
        )''',
        '''        self.assertEqual(
            derive_recommended_action(rows["protected"]),
            "candidate_review",
        )''',
    )
    text = text.replace(
        'self.assertEqual(projects["protected"].launch_policy["status"], "blocked")',
        'self.assertEqual(projects["protected"].launch_policy["status"], "eligible")',
    )
    text = text.replace(
        'self.assertEqual(projects["protected"].review_policy["status"], "manual_only")',
        'self.assertEqual(projects["protected"].review_policy["status"], "not_required")',
    )
    path.write_text(text, encoding="utf-8")


def main() -> int:
    migrate_source()
    migrate_tests()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
