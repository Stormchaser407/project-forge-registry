"""Shared Project Forge repository classification compatibility policy.

The former ``protected_manual_review`` category was created primarily to hide or
block Cerberus-labeled repositories. That project-name exception was retired on
2026-07-23. New discovery does not emit the category, but generated artifacts may
retain it until Legion performs a fresh scan.
"""

from __future__ import annotations

LEGACY_PROTECTED_CATEGORY = "protected_manual_review"
LEGACY_CERBERUS_WARNINGS = {
    "cerberus_special_case_candidate",
    "cerberus_name_requires_manual_reconciliation_review",
    "cerberus_related_project_requires_manual_review",
    "cerberus_protected",
}


def normalize_repo_category(
    category: str,
    git_status: str,
    has_project_forge_marker: bool,
) -> str:
    """Translate the retired protected category into ordinary repo state."""

    if category != LEGACY_PROTECTED_CATEGORY:
        return category
    if has_project_forge_marker:
        return "known_embedded"
    if git_status == "dirty":
        return "dirty_candidate_review_first"
    if git_status == "clean":
        return "clean_candidate"
    return "unknown_structure"


def remove_legacy_cerberus_warnings(warnings: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    """Drop name-based warnings while preserving real content/state warnings."""

    return tuple(item for item in warnings if item not in LEGACY_CERBERUS_WARNINGS)
