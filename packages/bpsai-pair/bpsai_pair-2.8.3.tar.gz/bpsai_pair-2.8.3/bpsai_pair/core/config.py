"""
Configuration management for PairCoder.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
import yaml
import json
from dataclasses import dataclass, asdict, field


# Current config version - update when schema changes
CURRENT_CONFIG_VERSION = "2.6"

# Required top-level sections for a complete config
REQUIRED_SECTIONS = [
    "version",
    "project",
    "workflow",
    "pack",
    "flows",
    "routing",
    "trello",
    "estimation",
    "metrics",
    "hooks",
    "security",
]


@dataclass
class ConfigValidationResult:
    """Result of config validation."""

    is_valid: bool
    current_version: Optional[str]
    target_version: str
    missing_sections: List[str]
    missing_keys: Dict[str, List[str]]  # section -> missing keys
    warnings: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "is_valid": self.is_valid,
            "current_version": self.current_version,
            "target_version": self.target_version,
            "missing_sections": self.missing_sections,
            "missing_keys": self.missing_keys,
            "warnings": self.warnings,
        }


def load_raw_config(root: Path) -> Tuple[Optional[Dict[str, Any]], Optional[Path]]:
    """Load raw config dictionary from file.

    Args:
        root: Project root directory

    Returns:
        Tuple of (config dict, config file path) or (None, None) if not found
    """
    config_file = Config.find_config_file(root)
    if not config_file or not config_file.exists():
        return None, None

    with open(config_file) as f:
        data = yaml.safe_load(f) or {}

    return data, config_file


def validate_config(root: Path, preset_name: str = "minimal") -> ConfigValidationResult:
    """Validate config against preset template.

    Args:
        root: Project root directory
        preset_name: Preset to validate against

    Returns:
        ConfigValidationResult with validation details
    """
    from .presets import get_preset

    raw_config, config_file = load_raw_config(root)

    if raw_config is None:
        return ConfigValidationResult(
            is_valid=False,
            current_version=None,
            target_version=CURRENT_CONFIG_VERSION,
            missing_sections=REQUIRED_SECTIONS,
            missing_keys={},
            warnings=["No config file found. Run 'bpsai-pair init' to create one."],
        )

    # Get template from preset
    preset = get_preset(preset_name)
    if not preset:
        preset = get_preset("minimal")

    template = preset.to_config_dict("Project", "Build software")

    # Check version
    current_version = raw_config.get("version")
    warnings = []

    if current_version and current_version != CURRENT_CONFIG_VERSION:
        warnings.append(f"Config version {current_version} is outdated (current: {CURRENT_CONFIG_VERSION})")

    # Check missing sections
    missing_sections = []
    for section in REQUIRED_SECTIONS:
        if section not in raw_config:
            missing_sections.append(section)

    # Check missing keys within existing sections
    missing_keys = {}
    for section, section_template in template.items():
        if section in raw_config and isinstance(section_template, dict) and isinstance(raw_config[section], dict):
            section_missing = []
            for key in section_template:
                if key not in raw_config[section]:
                    section_missing.append(key)
            if section_missing:
                missing_keys[section] = section_missing

    is_valid = not missing_sections and not missing_keys and not warnings

    return ConfigValidationResult(
        is_valid=is_valid,
        current_version=current_version,
        target_version=CURRENT_CONFIG_VERSION,
        missing_sections=missing_sections,
        missing_keys=missing_keys,
        warnings=warnings,
    )


def update_config(root: Path, preset_name: str = "minimal") -> Tuple[Dict[str, Any], List[str]]:
    """Update config with missing sections from preset.

    Args:
        root: Project root directory
        preset_name: Preset to use for defaults

    Returns:
        Tuple of (updated config dict, list of changes made)
    """
    from .presets import get_preset

    raw_config, config_file = load_raw_config(root)

    if raw_config is None:
        raise ValueError("No config file found. Run 'bpsai-pair init' first.")

    # Get template from preset
    preset = get_preset(preset_name)
    if not preset:
        preset = get_preset("minimal")

    # Get project name and goal from existing config
    project_name = raw_config.get("project", {}).get("name", "My Project")
    primary_goal = raw_config.get("project", {}).get("primary_goal", "Build software")

    template = preset.to_config_dict(project_name, primary_goal)

    changes = []

    # Update version
    old_version = raw_config.get("version")
    if old_version != CURRENT_CONFIG_VERSION:
        raw_config["version"] = CURRENT_CONFIG_VERSION
        changes.append(f"Updated version: {old_version} → {CURRENT_CONFIG_VERSION}")

    # Add missing sections
    for section in REQUIRED_SECTIONS:
        if section not in raw_config and section in template:
            raw_config[section] = template[section]
            changes.append(f"Added section: {section}")

    # Add missing keys within existing sections (preserve existing values)
    for section, section_template in template.items():
        if section in raw_config and isinstance(section_template, dict) and isinstance(raw_config[section], dict):
            for key, value in section_template.items():
                if key not in raw_config[section]:
                    raw_config[section][key] = value
                    changes.append(f"Added key: {section}.{key}")

    return raw_config, changes


def save_raw_config(root: Path, config: Dict[str, Any]) -> Path:
    """Save raw config dictionary to file.

    Args:
        root: Project root directory
        config: Config dictionary to save

    Returns:
        Path to saved config file
    """
    config_file = Config.find_config_file(root)
    if not config_file:
        # Default to v2 location
        config_dir = root / ".paircoder"
        config_dir.mkdir(exist_ok=True)
        config_file = config_dir / "config.yaml"

    with open(config_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    return config_file

@dataclass
class Config:
    """PairCoder configuration."""

    # Project settings
    project_name: str = "My Project"
    primary_goal: str = "Build awesome software"
    coverage_target: int = 80

    # Branch settings
    default_branch_type: str = "feature"
    main_branch: str = "main"

    # Context settings
    context_dir: str = "context"

    # Pack settings
    default_pack_name: str = "agent_pack.tgz"
    pack_excludes: list[str] = field(default_factory=lambda: [
        ".git", ".venv", "__pycache__", "node_modules",
        "dist", "build", "*.log", "*.bak"
    ])

    # CI settings
    python_formatter: str = "ruff"
    node_formatter: str = "prettier"

    @classmethod
    def find_config_file(cls, root: Path) -> Optional[Path]:
        """Find the config file, preferring v2 .paircoder/ folder over legacy .paircoder.yml."""
        # v2 config: .paircoder/config.yaml (preferred)
        v2_config = root / ".paircoder" / "config.yaml"
        if v2_config.exists():
            return v2_config

        # Also check .yml extension for v2
        v2_config_yml = root / ".paircoder" / "config.yml"
        if v2_config_yml.exists():
            return v2_config_yml

        # Legacy: .paircoder.yml (fallback)
        legacy_config = root / ".paircoder.yml"
        if legacy_config.exists():
            return legacy_config

        return None

    @classmethod
    def load(cls, root: Path) -> "Config":
        """Load configuration from .paircoder/config.yaml, .paircoder.yml, or environment.

        Config resolution order:
        1. .paircoder/config.yaml (v2 preferred)
        2. .paircoder/config.yml (v2 alternate)
        3. .paircoder.yml (legacy fallback)
        4. Environment variables (override all)
        """
        config_file = cls.find_config_file(root)

        data = {}
        if config_file and config_file.exists():
            with open(config_file) as f:
                yaml_data = yaml.safe_load(f) or {}

                # Handle both flat and nested structures
                if "version" in yaml_data:
                    # New nested structure
                    if "project" in yaml_data:
                        project = yaml_data["project"]
                        data["project_name"] = project.get("name", "My Project")
                        data["primary_goal"] = project.get("primary_goal", "Build awesome software")
                        data["coverage_target"] = project.get("coverage_target", 80)

                    if "workflow" in yaml_data:
                        workflow = yaml_data["workflow"]
                        data["default_branch_type"] = workflow.get("default_branch_type", "feature")
                        data["main_branch"] = workflow.get("main_branch", "main")
                        data["context_dir"] = workflow.get("context_dir", "context")

                    if "pack" in yaml_data:
                        pack = yaml_data["pack"]
                        data["default_pack_name"] = pack.get("default_name", "agent_pack.tgz")
                        data["pack_excludes"] = pack.get("excludes", [])

                    if "ci" in yaml_data:
                        ci = yaml_data["ci"]
                        data["python_formatter"] = ci.get("python_formatter", "ruff")
                        data["node_formatter"] = ci.get("node_formatter", "prettier")
                else:
                    # Old flat structure (backwards compatibility)
                    data = yaml_data

        # Override with environment variables
        env_mappings = {
            "PAIRCODER_MAIN_BRANCH": "main_branch",
            "PAIRCODER_CONTEXT_DIR": "context_dir",
            "PAIRCODER_DEFAULT_BRANCH": "default_branch_type",
            "PAIRCODER_PROJECT_NAME": "project_name",
        }

        for env_var, config_key in env_mappings.items():
            if env_value := os.getenv(env_var):
                data[config_key] = env_value

        # Create config with collected data
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})

    def save(self, root: Path, use_v2: bool = False, legacy: bool = False) -> Path:
        """Save configuration to config file.

        Args:
            root: Project root directory
            use_v2: If True, save to .paircoder/config.yaml (v2 format)
            legacy: If True, force save to .paircoder.yml (legacy format)

        Returns:
            Path to the saved config file

        Priority:
        1. If legacy=True, use .paircoder.yml
        2. If use_v2=True or .paircoder/ exists, use .paircoder/config.yaml
        3. Otherwise use .paircoder.yml (legacy default for compatibility)
        """
        if legacy:
            config_file = root / ".paircoder.yml"
        elif use_v2 or (root / ".paircoder").exists():
            config_dir = root / ".paircoder"
            config_dir.mkdir(exist_ok=True)
            config_file = config_dir / "config.yaml"
        else:
            config_file = root / ".paircoder.yml"

        data = {
            "version": "2" if use_v2 or config_file.parent.name == ".paircoder" else "0.1.3",
            "project": {
                "name": self.project_name,
                "primary_goal": self.primary_goal,
                "coverage_target": self.coverage_target,
            },
            "workflow": {
                "default_branch_type": self.default_branch_type,
                "main_branch": self.main_branch,
                "context_dir": self.context_dir,
            },
            "pack": {
                "default_name": self.default_pack_name,
                "excludes": self.pack_excludes,
            },
            "ci": {
                "python_formatter": self.python_formatter,
                "node_formatter": self.node_formatter,
            }
        }

        with open(config_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

        return config_file

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class ContextTemplate:
    """Templates for context files."""

    @staticmethod
    def development_md(config: Config) -> str:
        """Generate development.md template."""
        return f"""# Development Log

**Project:** {config.project_name}
**Phase:** Phase 1: Initial Setup
**Primary Goal:** {config.primary_goal}

## KPIs & Non-Functional Targets

- Test Coverage: ≥ {config.coverage_target}%
- Documentation: Complete for all public APIs
- Performance: Response time < 200ms (p95)

## Phase 1 — Foundation (Weeks 1–2)

**Objectives**
- Set up project structure and CI/CD
- Define core architecture and interfaces
- Establish testing framework

**Tasks**
- [ ] Initialize repository with PairCoder
- [ ] Set up CI workflows
- [ ] Create initial project structure
- [ ] Write architectural decision records

**Testing Plan**
- Unit tests for all business logic
- Integration tests for external boundaries
- End-to-end tests for critical user flows

**Risks & Rollback**
- Risk: Incomplete requirements — Mitigation: Regular stakeholder reviews
- Rollback: Git revert with documented rollback procedures

## Context Sync (AUTO-UPDATED)

- **Overall goal is:** {config.primary_goal}
- **Last action was:** Initialized project
- **Next action will be:** Set up CI/CD pipeline
- **Blockers:** None
"""

    @staticmethod
    def agents_md(config: Config) -> str:
        """Generate agents.md template."""
        return f"""# Agents Guide — AI Pair Coding Playbook

**Project:** {config.project_name}
**Purpose:** {config.primary_goal}

## Ground Rules

1. **Context is King**: Always refer to `.paircoder/context/state.md` for current state
2. **Test First**: Write tests before implementation
3. **Small Changes**: Keep PRs under 200 lines when possible
4. **Update Loop**: Run `bpsai-pair context-sync` after every significant change

## Project Structure (v2.1)

```
.
├── .paircoder/                    # All PairCoder configuration
│   ├── config.yaml               # Configuration
│   ├── context/                  # Project context (moved from root)
│   │   ├── state.md              # Current state
│   │   ├── project.md            # Project overview
│   │   └── workflow.md           # Development workflow
│   ├── flows/                    # Workflow definitions
│   ├── plans/                    # Plan files
│   └── tasks/                    # Task files
├── .claude/                       # Claude Code native (if used)
├── AGENTS.md                      # Universal entry point
├── CLAUDE.md                      # Claude Code pointer
├── src/                           # Source code
├── tests/                         # Test suites
└── docs/                          # Documentation
```

## Workflow

1. Check status: `bpsai-pair status`
2. Create feature: `bpsai-pair feature <name> --primary "<goal>" --phase "<phase>"`
3. Make changes (with tests)
4. Update context: `bpsai-pair context-sync --last "<what>" --next "<next>"`
5. Create pack: `bpsai-pair pack`
6. Share with AI agent

## Testing Requirements

- Minimum coverage: {config.coverage_target}%
- All new code must have tests
- Integration tests for external dependencies
- Performance tests for critical paths

## Code Style

- Python: {config.python_formatter} for formatting and linting
- JavaScript: {config.node_formatter} for formatting
- Commit messages: Conventional Commits format
- Branch names: {config.default_branch_type}/<description>

## Context Loop Protocol

After EVERY meaningful change:
```bash
bpsai-pair context-sync \\
    --last "What was just completed" \\
    --next "The immediate next step" \\
    --blockers "Any impediments"
```

## Excluded from Context

The following are excluded from agent packs (see `.agentpackignore`):
{chr(10).join(f'- {exclude}' for exclude in config.pack_excludes)}

## Commands Reference

- `bpsai-pair init` - Initialize scaffolding
- `bpsai-pair feature` - Create feature branch
- `bpsai-pair pack` - Create context package
- `bpsai-pair sync` - Update context loop
- `bpsai-pair status` - Show current state
- `bpsai-pair validate` - Check structure
- `bpsai-pair ci` - Run local CI checks
"""

    @staticmethod
    def gitignore() -> str:
        """Generate .gitignore template."""
        return """# PairCoder
.paircoder.yml.local
.paircoder/config.local.yaml
.paircoder/config.local.yml
agent_pack*.tgz
*.bak

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
ENV/
env/
*.egg-info/
dist/
build/
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage
htmlcov/

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.npm
.yarn-integrity

# IDE
.idea/
.vscode/
*.swp
*.swo
*~
.DS_Store

# Environment
.env
.env.local
.env.*.local

# Logs
*.log
logs/

# OS
Thumbs.db
Desktop.ini
"""
