"""Project Forge configuration model and loader.

This module provides a machine-agnostic configuration model for the Project Forge
registry system. It supports loading YAML configuration files, validating required
fields, providing safe defaults, and enforcing safety policies.

Safety Policy:
- allow_apply and allow_push are rejected unless explicitly supported by future policy
- Paths are expanded (~) but not required to exist by default
- Local configuration files (config/project_forge.local.yml) must be git-ignored
"""

from __future__ import annotations

import os
import re
from dataclasses import asdict, dataclass, field
from io import StringIO
from pathlib import Path
from typing import Any

# Try to import yaml, but keep a stdlib fallback parser for simple configs
try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment,misc]


class ConfigError(Exception):
    """Base exception for configuration errors."""

    pass


class ConfigValidationError(ConfigError):
    """Raised when configuration validation fails."""

    pass


class ConfigPolicyError(ConfigError):
    """Raised when configuration violates safety policy."""

    pass


class SimpleConfigParseError(ConfigError):
    """Raised when the limited stdlib config parser encounters invalid input."""

    pass


@dataclass(slots=True)
class ProjectForgeConfig:
    """Configuration model for Project Forge registry.

    Attributes:
        projects_root: Root directory for project storage. Required.
        vault_project_root: Root directory for Obsidian vault projects. Required.
        default_slug: Default slug for new projects.
        editor_command: Command to open editor (e.g., "code", "nvim").
        dashboard_host: Host for dashboard server (default: "127.0.0.1").
        dashboard_port: Port for dashboard server (default: 8080).
        theme: UI theme name (default: "dark").
        scan_roots: List of directories to scan for projects.
        excluded_paths: List of paths to exclude from scanning.
        allow_apply: Whether to allow apply operations (currently rejected by policy).
        allow_push: Whether to allow push operations (currently rejected by policy).
    """

    projects_root: str
    vault_project_root: str
    default_slug: str | None = None
    editor_command: str | None = None
    dashboard_host: str = "127.0.0.1"
    dashboard_port: int = 8080
    theme: str = "dark"
    scan_roots: list[str] = field(default_factory=list)
    excluded_paths: list[str] = field(default_factory=list)
    allow_apply: bool = False
    allow_push: bool = False

    # Internal flag for validation mode
    _validate_paths_exist: bool = False

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        self._validate()

    def _validate(self) -> None:
        """Validate configuration values.

        Raises:
            ConfigValidationError: If required fields are missing or invalid.
            ConfigPolicyError: If configuration violates safety policy.
        """
        # Validate required fields
        if not self.projects_root:
            raise ConfigValidationError("projects_root is required")
        if not self.vault_project_root:
            raise ConfigValidationError("vault_project_root is required")

        # Validate types
        if not isinstance(self.dashboard_port, int):
            raise ConfigValidationError("dashboard_port must be an integer")
        if self.dashboard_port < 1 or self.dashboard_port > 65535:
            raise ConfigValidationError("dashboard_port must be between 1 and 65535")

        # Validate theme
        valid_themes = {"dark", "light", "system"}
        if self.theme not in valid_themes:
            raise ConfigValidationError(f"theme must be one of: {valid_themes}")

        # Safety policy: reject allow_apply and allow_push
        if self.allow_apply:
            raise ConfigPolicyError(
                "allow_apply=true is not supported by current safety policy. "
                "This feature requires explicit policy approval."
            )
        if self.allow_push:
            raise ConfigPolicyError(
                "allow_push=true is not supported by current safety policy. "
                "This feature requires explicit policy approval."
            )

        # Validate paths exist if in validation mode
        if self._validate_paths_exist:
            self._validate_paths_existence()

    def _validate_paths_existence(self) -> None:
        """Validate that required paths exist.

        Raises:
            ConfigValidationError: If required paths do not exist.
        """
        projects_path = self.get_projects_root()
        if projects_path and not projects_path.exists():
            raise ConfigValidationError(
                f"projects_root does not exist: {projects_path}"
            )

        vault_path = self.get_vault_project_root()
        if vault_path and not vault_path.exists():
            raise ConfigValidationError(
                f"vault_project_root does not exist: {vault_path}"
            )

    def get_projects_root(self) -> Path | None:
        """Get projects_root as an expanded Path object.

        Returns:
            Expanded Path or None if not set.
        """
        if not self.projects_root:
            return None
        return Path(os.path.expanduser(self.projects_root)).resolve()

    def get_vault_project_root(self) -> Path | None:
        """Get vault_project_root as an expanded Path object.

        Returns:
            Expanded Path or None if not set.
        """
        if not self.vault_project_root:
            return None
        return Path(os.path.expanduser(self.vault_project_root)).resolve()

    def get_scan_roots(self) -> list[Path]:
        """Get scan_roots as a list of expanded Path objects.

        Returns:
            List of expanded Paths.
        """
        return [
            Path(os.path.expanduser(root)).resolve()
            for root in self.scan_roots
            if root
        ]

    def get_excluded_paths(self) -> list[Path]:
        """Get excluded_paths as a list of expanded Path objects.

        Returns:
            List of expanded Paths.
        """
        return [
            Path(os.path.expanduser(path)).resolve()
            for path in self.excluded_paths
            if path
        ]

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to a dictionary.

        Returns:
            Dictionary representation of the configuration.
        """
        result = asdict(self)
        # Remove internal fields
        result.pop("_validate_paths_exist", None)
        return result


class ConfigLoader:
    """Loader for Project Forge configuration files.

    This class handles loading YAML configuration files and merging them
    with defaults to produce a validated ProjectForgeConfig instance.
    """

    # Default configuration values
    DEFAULTS: dict[str, Any] = {
        "dashboard_host": "127.0.0.1",
        "dashboard_port": 8080,
        "theme": "dark",
        "scan_roots": [],
        "excluded_paths": [],
        "allow_apply": False,
        "allow_push": False,
    }

    # Required configuration keys
    REQUIRED_KEYS: set[str] = {"projects_root", "vault_project_root"}

    def __init__(self, validate_paths: bool = False) -> None:
        """Initialize the config loader.

        Args:
            validate_paths: If True, validate that paths exist during loading.
        """
        self.validate_paths = validate_paths

    def load(self, path: str | Path) -> ProjectForgeConfig:
        """Load configuration from a YAML file.

        Args:
            path: Path to the YAML configuration file.

        Returns:
            Validated ProjectForgeConfig instance.

        Raises:
            ConfigError: If the file cannot be read or parsed.
            ConfigValidationError: If required fields are missing.
            ConfigPolicyError: If configuration violates safety policy.
        """
        path = Path(path)

        if not path.exists():
            raise ConfigError(f"Configuration file not found: {path}")

        try:
            content = path.read_text(encoding="utf-8")
            data = self._parse_yaml(content)
        except Exception as e:
            raise ConfigError(f"Failed to read configuration file: {e}") from e

        return self._build_config(data)

    def load_string(self, content: str) -> ProjectForgeConfig:
        """Load configuration from a YAML string.

        Args:
            content: YAML configuration content.

        Returns:
            Validated ProjectForgeConfig instance.

        Raises:
            ConfigError: If the content cannot be parsed.
            ConfigValidationError: If required fields are missing.
            ConfigPolicyError: If configuration violates safety policy.
        """
        data = self._parse_yaml(content)
        return self._build_config(data)

    def _parse_yaml(self, content: str) -> dict[str, Any]:
        """Parse YAML content with optional PyYAML support and stdlib fallback.

        Args:
            content: YAML content string or file-like object.

        Returns:
            Parsed dictionary.

        Raises:
            ConfigError: If YAML parsing fails.
        """
        if yaml is not None:
            try:
                result = yaml.safe_load(content)
                if result is None:
                    return {}
                if not isinstance(result, dict):
                    raise ConfigError(
                        "Configuration must be a YAML mapping (dictionary)"
                    )
                return result
            except yaml.YAMLError as e:
                raise ConfigError(f"Invalid YAML: {e}") from e

        return self._parse_simple_yaml(content)

    def _parse_simple_yaml(self, content: str) -> dict[str, Any]:
        """Parse the limited Project Forge config format with stdlib only."""
        data: dict[str, Any] = {}
        current_list_key: str | None = None

        for line_number, raw_line in enumerate(StringIO(content), start=1):
            line = self._strip_inline_comment(raw_line.rstrip("\n"))
            if not line.strip():
                continue

            if line.startswith((" ", "\t")):
                stripped = line.strip()
                if not stripped.startswith("- "):
                    raise SimpleConfigParseError(
                        f"Invalid config at line {line_number}: unexpected indentation"
                    )
                if current_list_key is None:
                    raise SimpleConfigParseError(
                        f"Invalid config at line {line_number}: list item without a list key"
                    )
                if data[current_list_key] is None:
                    data[current_list_key] = []
                list_value = stripped[2:].strip()
                data[current_list_key].append(self._parse_scalar(list_value))
                continue

            current_list_key = None
            stripped = line.strip()
            if stripped.startswith("- "):
                raise ConfigError("Configuration must be a YAML mapping (dictionary)")

            if ":" not in stripped:
                raise SimpleConfigParseError(
                    f"Invalid config at line {line_number}: expected 'key: value'"
                )

            key, raw_value = stripped.split(":", 1)
            key = key.strip()
            if not key:
                raise SimpleConfigParseError(
                    f"Invalid config at line {line_number}: empty key"
                )

            value = raw_value.strip()
            if not value:
                data[key] = None
                current_list_key = key
                continue

            data[key] = self._parse_scalar(value)

        return data

    def _strip_inline_comment(self, line: str) -> str:
        """Remove comments while respecting quoted strings."""
        result: list[str] = []
        quote: str | None = None

        for char in line:
            if char in {'"', "'"}:
                if quote is None:
                    quote = char
                elif quote == char:
                    quote = None
            if char == "#" and quote is None:
                break
            result.append(char)

        return "".join(result).rstrip()

    def _parse_scalar(self, value: str) -> Any:
        """Parse a limited scalar value from the fallback config format."""
        if value == "":
            return None

        lowered = value.lower()
        if lowered == "true":
            return True
        if lowered == "false":
            return False
        if lowered in {"null", "~"}:
            return None
        if re.fullmatch(r"[+-]?\d+", value):
            return int(value)
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            return value[1:-1]
        return value

    def _coerce_bool(self, value: Any, key: str) -> bool:
        """Coerce a config value to bool with clear validation."""
        if isinstance(value, bool):
            return value
        if value is None:
            return False
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered == "true":
                return True
            if lowered == "false":
                return False
        raise ConfigValidationError(f"{key} must be a boolean")

    def _build_config(self, data: dict[str, Any]) -> ProjectForgeConfig:
        """Build a config instance from parsed data.

        Args:
            data: Parsed YAML data.

        Returns:
            Validated ProjectForgeConfig instance.

        Raises:
            ConfigValidationError: If required fields are missing.
            ConfigPolicyError: If configuration violates safety policy.
        """
        # Check for required keys
        missing = self.REQUIRED_KEYS - set(data.keys())
        if missing:
            raise ConfigValidationError(
                f"Missing required configuration keys: {sorted(missing)}"
            )

        # Merge with defaults
        merged = {**self.DEFAULTS, **data}

        # Ensure list fields are lists
        for key in ("scan_roots", "excluded_paths"):
            if not isinstance(merged.get(key), list):
                merged[key] = []

        # Create config with validation
        config = ProjectForgeConfig(
            projects_root=str(merged["projects_root"]),
            vault_project_root=str(merged["vault_project_root"]),
            default_slug=merged.get("default_slug"),
            editor_command=merged.get("editor_command"),
            dashboard_host=str(merged.get("dashboard_host", "127.0.0.1")),
            dashboard_port=int(merged.get("dashboard_port", 8080)),
            theme=str(merged.get("theme", "dark")),
            scan_roots=[str(s) for s in merged.get("scan_roots", [])],
            excluded_paths=[str(e) for e in merged.get("excluded_paths", [])],
            allow_apply=self._coerce_bool(merged.get("allow_apply", False), "allow_apply"),
            allow_push=self._coerce_bool(merged.get("allow_push", False), "allow_push"),
        )

        # Set internal validation flag
        config._validate_paths_exist = self.validate_paths

        # Re-validate with path existence check if enabled
        if self.validate_paths:
            config._validate()

        return config


def load_config(path: str | Path, validate_paths: bool = False) -> ProjectForgeConfig:
    """Convenience function to load configuration from a file.

    Args:
        path: Path to the YAML configuration file.
        validate_paths: If True, validate that paths exist.

    Returns:
        Validated ProjectForgeConfig instance.

    Raises:
        ConfigError: If the file cannot be read or parsed.
        ConfigValidationError: If required fields are missing.
        ConfigPolicyError: If configuration violates safety policy.
    """
    loader = ConfigLoader(validate_paths=validate_paths)
    return loader.load(path)


def get_default_config_path() -> Path:
    """Get the default configuration file path.

    Returns:
        Path to the default configuration file.
    """
    # Look for config in common locations
    candidates = [
        Path("config/project_forge.yml"),
        Path("config/project_forge.local.yml"),
        Path("project_forge.yml"),
        Path.home() / ".config" / "project-forge" / "config.yml",
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    # Return the first candidate as the default location
    return candidates[0]
