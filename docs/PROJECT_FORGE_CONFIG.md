# Project Forge Configuration Reference

This document describes the configuration schema for the Project Forge Registry system.

## Overview

Project Forge uses a YAML configuration file to define project storage locations, dashboard settings, scanning behavior, and safety policies. The configuration model is machine-agnostic and designed to be portable across different environments.

## Configuration File Locations

The system looks for configuration files in the following order:

1. `config/project_forge.yml` — Main configuration (can be committed)
2. `config/project_forge.local.yml` — Local overrides (should be git-ignored)
3. `project_forge.yml` — Root-level configuration
4. `~/.config/project-forge/config.yml` — User-level configuration

**Recommended setup:** Copy `config/project_forge.example.yml` to `config/project_forge.local.yml` and customize. The `.gitignore` file should include `config/project_forge.local.yml` to prevent committing sensitive paths.

## Schema Reference

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `projects_root` | string | Root directory for project storage. Supports `~` expansion. |
| `vault_project_root` | string | Root directory for Obsidian vault projects. Supports `~` expansion. |

### Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `default_slug` | string | `null` | Default slug for new projects. |
| `editor_command` | string | `null` | Command to open the code editor (e.g., `code`, `nvim`). |
| `dashboard_host` | string | `127.0.0.1` | Host for the dashboard web server. |
| `dashboard_port` | integer | `8080` | Port for the dashboard web server (1-65535). |
| `theme` | string | `dark` | UI theme: `dark`, `light`, or `system`. |
| `scan_roots` | list[string] | `[]` | Directories to scan for projects. |
| `excluded_paths` | list[string] | `[]` | Paths to exclude from scanning. |
| `allow_apply` | boolean | `false` | Allow apply operations (currently rejected by policy). |
| `allow_push` | boolean | `false` | Allow push operations (currently rejected by policy). |

## Example Configuration

```yaml
# Required: Project Storage
projects_root: ~/Projects
vault_project_root: ~/main_vault/10 Projects

# Optional: Project Defaults
# default_slug: my-project
# editor_command: code

# Optional: Dashboard Settings
# dashboard_host: 127.0.0.1
# dashboard_port: 8080
# theme: dark

# Optional: Scanning Configuration
# scan_roots:
#   - ~/Projects
#   - ~/work
# excluded_paths:
#   - ~/Projects/archive

# Safety Policy (do not enable without explicit approval)
# allow_apply: false
# allow_push: false
```

## Validation Rules

### Required Field Validation

The configuration loader validates that `projects_root` and `vault_project_root` are present and non-empty. Missing required fields raise `ConfigValidationError`.

### Type Validation

- `dashboard_port` must be an integer between 1 and 65535.
- `theme` must be one of: `dark`, `light`, `system`.
- `scan_roots` and `excluded_paths` must be lists (non-list values are coerced to empty lists).

### Path Expansion

All path fields support `~` for home directory expansion. Paths are expanded when accessed via the `get_*` methods on the config object.

### Path Existence Validation

By default, paths are **not** required to exist. This allows configuration to be loaded on machines where certain directories may not yet be created. To enable path existence validation, pass `validate_paths=True` to the `ConfigLoader`.

## Safety Policy

### Restricted Operations

The following settings are **rejected** by the current safety policy:

- `allow_apply: true` — Raises `ConfigPolicyError`
- `allow_push: true` — Raises `ConfigPolicyError`

These features require explicit policy approval before they can be enabled. This is a deliberate safety mechanism to prevent accidental destructive operations.

### Exception Hierarchy

```
ConfigError (base)
├── ConfigValidationError — Missing/invalid configuration values
└── ConfigPolicyError — Safety policy violations
```

## Programmatic Usage

### Loading Configuration

```python
from project_forge_registry.config_model import load_config, ConfigLoader

# Convenience function
config = load_config("config/project_forge.local.yml")

# With path existence validation
config = load_config("config/project_forge.local.yml", validate_paths=True)

# Using ConfigLoader directly
loader = ConfigLoader(validate_paths=False)
config = loader.load("config/project_forge.local.yml")

# From a string (useful for testing)
config = loader.load_string(yaml_content)
```

### Accessing Configuration

```python
# Get expanded paths
projects_path = config.get_projects_root()  # Returns Path | None
vault_path = config.get_vault_project_root()  # Returns Path | None
scan_paths = config.get_scan_roots()  # Returns list[Path]
excluded = config.get_excluded_paths()  # Returns list[Path]

# Direct attribute access (raw strings)
print(config.projects_root)
print(config.dashboard_port)

# Convert to dictionary
config_dict = config.to_dict()
```

### Direct Instantiation

```python
from project_forge_registry.config_model import ProjectForgeConfig

config = ProjectForgeConfig(
    projects_root="/home/user/Projects",
    vault_project_root="/home/user/vault/Projects",
    dashboard_port=3000,
    theme="light",
)
```

## Local Configuration and Git

The file `config/project_forge.local.yml` should be added to `.gitignore` to prevent committing local paths and settings. The example file `config/project_forge.example.yml` is safe to commit and serves as a template.

Example `.gitignore` entry:

```gitignore
# Local Project Forge configuration
config/project_forge.local.yml
```

## See Also

- `config/project_forge.example.yml` — Example configuration file with all fields documented
- `src/project_forge_registry/config_model.py` — Implementation source code
- `tests/test_config_model.py` — Test suite with additional usage examples