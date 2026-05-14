from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from project_forge_registry.config_model import (
    ConfigError,
    ConfigLoader,
    ConfigPolicyError,
    ConfigValidationError,
    ProjectForgeConfig,
    get_default_config_path,
    load_config,
)


class ProjectForgeConfigTests(unittest.TestCase):
    """Tests for ProjectForgeConfig dataclass."""

    def test_config_creation_with_required_fields(self) -> None:
        config = ProjectForgeConfig(
            projects_root="/home/user/Projects",
            vault_project_root="/home/user/vault/Projects",
        )

        self.assertEqual(config.projects_root, "/home/user/Projects")
        self.assertEqual(config.vault_project_root, "/home/user/vault/Projects")
        self.assertIsNone(config.default_slug)
        self.assertIsNone(config.editor_command)
        self.assertEqual(config.dashboard_host, "127.0.0.1")
        self.assertEqual(config.dashboard_port, 8080)
        self.assertEqual(config.theme, "dark")
        self.assertEqual(config.scan_roots, [])
        self.assertEqual(config.excluded_paths, [])
        self.assertFalse(config.allow_apply)
        self.assertFalse(config.allow_push)

    def test_config_creation_with_all_fields(self) -> None:
        config = ProjectForgeConfig(
            projects_root="/home/user/Projects",
            vault_project_root="/home/user/vault/Projects",
            default_slug="my-project",
            editor_command="code",
            dashboard_host="0.0.0.0",
            dashboard_port=3000,
            theme="light",
            scan_roots=["/home/user/Projects", "/home/user/work"],
            excluded_paths=["/home/user/Projects/archive"],
            allow_apply=False,
            allow_push=False,
        )

        self.assertEqual(config.projects_root, "/home/user/Projects")
        self.assertEqual(config.vault_project_root, "/home/user/vault/Projects")
        self.assertEqual(config.default_slug, "my-project")
        self.assertEqual(config.editor_command, "code")
        self.assertEqual(config.dashboard_host, "0.0.0.0")
        self.assertEqual(config.dashboard_port, 3000)
        self.assertEqual(config.theme, "light")
        self.assertEqual(config.scan_roots, ["/home/user/Projects", "/home/user/work"])
        self.assertEqual(config.excluded_paths, ["/home/user/Projects/archive"])
        self.assertFalse(config.allow_apply)
        self.assertFalse(config.allow_push)

    def test_config_rejects_empty_projects_root(self) -> None:
        with self.assertRaises(ConfigValidationError) as ctx:
            ProjectForgeConfig(
                projects_root="",
                vault_project_root="/home/user/vault/Projects",
            )
        self.assertIn("projects_root is required", str(ctx.exception))

    def test_config_rejects_empty_vault_project_root(self) -> None:
        with self.assertRaises(ConfigValidationError) as ctx:
            ProjectForgeConfig(
                projects_root="/home/user/Projects",
                vault_project_root="",
            )
        self.assertIn("vault_project_root is required", str(ctx.exception))

    def test_config_rejects_invalid_port_low(self) -> None:
        with self.assertRaises(ConfigValidationError) as ctx:
            ProjectForgeConfig(
                projects_root="/home/user/Projects",
                vault_project_root="/home/user/vault/Projects",
                dashboard_port=0,
            )
        self.assertIn("dashboard_port must be between 1 and 65535", str(ctx.exception))

    def test_config_rejects_invalid_port_high(self) -> None:
        with self.assertRaises(ConfigValidationError) as ctx:
            ProjectForgeConfig(
                projects_root="/home/user/Projects",
                vault_project_root="/home/user/vault/Projects",
                dashboard_port=99999,
            )
        self.assertIn("dashboard_port must be between 1 and 65535", str(ctx.exception))

    def test_config_rejects_invalid_theme(self) -> None:
        with self.assertRaises(ConfigValidationError) as ctx:
            ProjectForgeConfig(
                projects_root="/home/user/Projects",
                vault_project_root="/home/user/vault/Projects",
                theme="invalid_theme",
            )
        self.assertIn("theme must be one of:", str(ctx.exception))

    def test_config_accepts_valid_themes(self) -> None:
        for theme in ("dark", "light", "system"):
            config = ProjectForgeConfig(
                projects_root="/home/user/Projects",
                vault_project_root="/home/user/vault/Projects",
                theme=theme,
            )
            self.assertEqual(config.theme, theme)

    def test_config_rejects_allow_apply_true(self) -> None:
        with self.assertRaises(ConfigPolicyError) as ctx:
            ProjectForgeConfig(
                projects_root="/home/user/Projects",
                vault_project_root="/home/user/vault/Projects",
                allow_apply=True,
            )
        self.assertIn("allow_apply=true is not supported", str(ctx.exception))

    def test_config_rejects_allow_push_true(self) -> None:
        with self.assertRaises(ConfigPolicyError) as ctx:
            ProjectForgeConfig(
                projects_root="/home/user/Projects",
                vault_project_root="/home/user/vault/Projects",
                allow_push=True,
            )
        self.assertIn("allow_push=true is not supported", str(ctx.exception))

    def test_get_projects_root_expands_user(self) -> None:
        config = ProjectForgeConfig(
            projects_root="~/Projects",
            vault_project_root="/home/user/vault/Projects",
        )

        path = config.get_projects_root()
        self.assertIsNotNone(path)
        # Should be expanded and resolved
        self.assertFalse(str(path).startswith("~"))

    def test_get_vault_project_root_expands_user(self) -> None:
        config = ProjectForgeConfig(
            projects_root="/home/user/Projects",
            vault_project_root="~/vault/Projects",
        )

        path = config.get_vault_project_root()
        self.assertIsNotNone(path)
        # Should be expanded and resolved
        self.assertFalse(str(path).startswith("~"))

    def test_get_scan_roots_expands_user(self) -> None:
        config = ProjectForgeConfig(
            projects_root="/home/user/Projects",
            vault_project_root="/home/user/vault/Projects",
            scan_roots=["~/Projects", "~/work"],
        )

        paths = config.get_scan_roots()
        self.assertEqual(len(paths), 2)
        for path in paths:
            self.assertFalse(str(path).startswith("~"))

    def test_get_excluded_paths_expands_user(self) -> None:
        config = ProjectForgeConfig(
            projects_root="/home/user/Projects",
            vault_project_root="/home/user/vault/Projects",
            excluded_paths=["~/Projects/archive"],
        )

        paths = config.get_excluded_paths()
        self.assertEqual(len(paths), 1)
        self.assertFalse(str(paths[0]).startswith("~"))

    def test_to_dict_excludes_internal_fields(self) -> None:
        config = ProjectForgeConfig(
            projects_root="/home/user/Projects",
            vault_project_root="/home/user/vault/Projects",
        )

        result = config.to_dict()

        self.assertNotIn("_validate_paths_exist", result)
        self.assertIn("projects_root", result)
        self.assertIn("vault_project_root", result)

    def test_validate_paths_existence_fails_for_missing_projects_root(self) -> None:
        config = ProjectForgeConfig(
            projects_root="/nonexistent/path/that/does/not/exist",
            vault_project_root="/home/user/vault/Projects",
        )
        config._validate_paths_exist = True

        with self.assertRaises(ConfigValidationError) as ctx:
            config._validate()
        self.assertIn("projects_root does not exist", str(ctx.exception))

    def test_validate_paths_existence_fails_for_missing_vault_root(self) -> None:
        import tempfile

        # Use a real temp directory for projects_root so vault_root is the only failure
        with tempfile.TemporaryDirectory() as tmp:
            config = ProjectForgeConfig(
                projects_root=str(tmp),
                vault_project_root="/nonexistent/path/that/does/not/exist",
            )
            config._validate_paths_exist = True

            with self.assertRaises(ConfigValidationError) as ctx:
                config._validate()
            self.assertIn("vault_project_root does not exist", str(ctx.exception))


class ConfigLoaderTests(unittest.TestCase):
    """Tests for ConfigLoader class."""

    def setUp(self) -> None:
        # Skip tests if yaml is not available
        try:
            import yaml  # noqa: F401
        except ImportError:
            self.skipTest("PyYAML not installed")

    def test_load_valid_config(self) -> None:
        yaml_content = """
projects_root: ~/Projects
vault_project_root: ~/vault/Projects
"""
        loader = ConfigLoader()
        config = loader.load_string(yaml_content)

        self.assertEqual(config.projects_root, "~/Projects")
        self.assertEqual(config.vault_project_root, "~/vault/Projects")
        self.assertEqual(config.dashboard_host, "127.0.0.1")
        self.assertEqual(config.dashboard_port, 8080)
        self.assertEqual(config.theme, "dark")
        self.assertFalse(config.allow_apply)
        self.assertFalse(config.allow_push)

    def test_load_config_with_all_fields(self) -> None:
        yaml_content = """
projects_root: ~/Projects
vault_project_root: ~/vault/Projects
default_slug: my-project
editor_command: nvim
dashboard_host: 0.0.0.0
dashboard_port: 3000
theme: light
scan_roots:
  - ~/Projects
  - ~/work
excluded_paths:
  - ~/Projects/archive
"""
        loader = ConfigLoader()
        config = loader.load_string(yaml_content)

        self.assertEqual(config.projects_root, "~/Projects")
        self.assertEqual(config.vault_project_root, "~/vault/Projects")
        self.assertEqual(config.default_slug, "my-project")
        self.assertEqual(config.editor_command, "nvim")
        self.assertEqual(config.dashboard_host, "0.0.0.0")
        self.assertEqual(config.dashboard_port, 3000)
        self.assertEqual(config.theme, "light")
        self.assertEqual(config.scan_roots, ["~/Projects", "~/work"])
        self.assertEqual(config.excluded_paths, ["~/Projects/archive"])

    def test_load_missing_required_fields(self) -> None:
        yaml_content = """
projects_root: ~/Projects
"""
        loader = ConfigLoader()

        with self.assertRaises(ConfigValidationError) as ctx:
            loader.load_string(yaml_content)
        self.assertIn("vault_project_root", str(ctx.exception))

    def test_load_missing_all_required_fields(self) -> None:
        yaml_content = """
theme: dark
"""
        loader = ConfigLoader()

        with self.assertRaises(ConfigValidationError) as ctx:
            loader.load_string(yaml_content)
        self.assertIn("Missing required configuration keys", str(ctx.exception))

    def test_load_rejects_allow_apply_true(self) -> None:
        yaml_content = """
projects_root: ~/Projects
vault_project_root: ~/vault/Projects
allow_apply: true
"""
        loader = ConfigLoader()

        with self.assertRaises(ConfigPolicyError) as ctx:
            loader.load_string(yaml_content)
        self.assertIn("allow_apply=true is not supported", str(ctx.exception))

    def test_load_rejects_allow_push_true(self) -> None:
        yaml_content = """
projects_root: ~/Projects
vault_project_root: ~/vault/Projects
allow_push: true
"""
        loader = ConfigLoader()

        with self.assertRaises(ConfigPolicyError) as ctx:
            loader.load_string(yaml_content)
        self.assertIn("allow_push=true is not supported", str(ctx.exception))

    def test_load_invalid_yaml(self) -> None:
        yaml_content = """
projects_root: ~/Projects
  invalid: yaml: content
    broken: yes
"""
        loader = ConfigLoader()

        with self.assertRaises(ConfigError) as ctx:
            loader.load_string(yaml_content)
        self.assertIn("Invalid YAML", str(ctx.exception))

    def test_load_non_dict_yaml(self) -> None:
        yaml_content = """
- item1
- item2
"""
        loader = ConfigLoader()

        with self.assertRaises(ConfigError) as ctx:
            loader.load_string(yaml_content)
        self.assertIn("must be a YAML mapping", str(ctx.exception))

    def test_load_file_not_found(self) -> None:
        loader = ConfigLoader()

        with self.assertRaises(ConfigError) as ctx:
            loader.load("/nonexistent/config/path.yml")
        self.assertIn("Configuration file not found", str(ctx.exception))

    def test_load_file_success(self) -> None:
        import tempfile

        yaml_content = """
projects_root: ~/Projects
vault_project_root: ~/vault/Projects
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yml", delete=False
        ) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name

        try:
            loader = ConfigLoader()
            config = loader.load(temp_path)

            self.assertEqual(config.projects_root, "~/Projects")
            self.assertEqual(config.vault_project_root, "~/vault/Projects")
        finally:
            import os

            os.unlink(temp_path)

    def test_load_validates_paths_when_enabled(self) -> None:
        yaml_content = """
projects_root: ~/Projects
vault_project_root: ~/vault/Projects
"""
        loader = ConfigLoader(validate_paths=False)
        # Should not raise even if paths don't exist
        config = loader.load_string(yaml_content)
        self.assertIsNotNone(config)

    def test_load_coerces_non_list_to_empty_list(self) -> None:
        yaml_content = """
projects_root: ~/Projects
vault_project_root: ~/vault/Projects
scan_roots: not_a_list
excluded_paths: 123
"""
        loader = ConfigLoader()
        config = loader.load_string(yaml_content)

        self.assertEqual(config.scan_roots, [])
        self.assertEqual(config.excluded_paths, [])


class LoadConfigFunctionTests(unittest.TestCase):
    """Tests for the load_config convenience function."""

    def setUp(self) -> None:
        try:
            import yaml  # noqa: F401
        except ImportError:
            self.skipTest("PyYAML not installed")

    def test_load_config_convenience_function(self) -> None:
        import tempfile

        yaml_content = """
projects_root: ~/Projects
vault_project_root: ~/vault/Projects
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yml", delete=False
        ) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name

        try:
            config = load_config(temp_path)
            self.assertEqual(config.projects_root, "~/Projects")
        finally:
            import os

            os.unlink(temp_path)


class GetDefaultConfigPathTests(unittest.TestCase):
    """Tests for get_default_config_path function."""

    @patch("pathlib.Path.exists")
    def test_returns_first_existing_candidate(self, mock_exists: unittest.mock.Mock) -> None:
        # Simulate: first doesn't exist, second exists
        mock_exists.side_effect = [False, True, False, False]

        result = get_default_config_path()

        # Should return the second candidate (config/project_forge.local.yml)
        self.assertEqual(result, Path("config/project_forge.local.yml"))

    @patch("pathlib.Path.exists")
    def test_returns_first_candidate_if_none_exist(self, mock_exists: unittest.mock.Mock) -> None:
        # Simulate: none exist
        mock_exists.side_effect = [False, False, False, False]

        result = get_default_config_path()

        # Should return the first candidate as default location
        self.assertEqual(result, Path("config/project_forge.yml"))


if __name__ == "__main__":
    unittest.main()