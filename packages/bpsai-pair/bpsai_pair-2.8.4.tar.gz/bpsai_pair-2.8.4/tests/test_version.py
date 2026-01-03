"""Tests for version string single source of truth.

Ensures version is read from pyproject.toml via importlib.metadata,
not hardcoded in __init__.py.
"""

import re
from pathlib import Path

import pytest


class TestVersionSingleSourceOfTruth:
    """Tests ensuring version comes from pyproject.toml only."""

    def test_version_matches_pyproject_toml(self):
        """Version in __init__.py matches pyproject.toml."""
        import bpsai_pair

        # Read version from pyproject.toml
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        pyproject_content = pyproject_path.read_text()

        # Extract version using regex
        version_match = re.search(r'^version\s*=\s*"([^"]+)"', pyproject_content, re.MULTILINE)
        assert version_match, "Could not find version in pyproject.toml"
        pyproject_version = version_match.group(1)

        # Compare with package version
        assert bpsai_pair.__version__ == pyproject_version, (
            f"Version mismatch: __init__.py has {bpsai_pair.__version__!r}, "
            f"pyproject.toml has {pyproject_version!r}"
        )

    def test_no_hardcoded_version_in_init(self):
        """__init__.py does not contain hardcoded version string."""
        init_path = Path(__file__).parent.parent / "bpsai_pair" / "__init__.py"
        init_content = init_path.read_text()

        # Check for hardcoded version patterns like __version__ = "2.6.0"
        hardcoded_pattern = re.compile(r'__version__\s*=\s*["\'][0-9]+\.[0-9]+\.[0-9]+["\']')
        assert not hardcoded_pattern.search(init_content), (
            "Found hardcoded version string in __init__.py. "
            "Version should be read from importlib.metadata."
        )

    def test_version_uses_importlib_metadata(self):
        """__init__.py uses importlib.metadata for version."""
        init_path = Path(__file__).parent.parent / "bpsai_pair" / "__init__.py"
        init_content = init_path.read_text()

        # Check for importlib.metadata import
        assert "from importlib.metadata import" in init_content or "import importlib.metadata" in init_content, (
            "__init__.py should import from importlib.metadata"
        )

        # Check for version() call
        assert 'version("bpsai-pair")' in init_content or "version('bpsai-pair')" in init_content, (
            "__init__.py should call version('bpsai-pair') from importlib.metadata"
        )

    def test_cli_version_command(self):
        """CLI --version flag shows correct version."""
        from typer.testing import CliRunner

        from bpsai_pair.cli import app

        runner = CliRunner()
        result = runner.invoke(app, ["--version"])

        assert result.exit_code == 0, f"--version failed: {result.output}"

        # Read expected version from pyproject.toml
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        pyproject_content = pyproject_path.read_text()
        version_match = re.search(r'^version\s*=\s*"([^"]+)"', pyproject_content, re.MULTILINE)
        expected_version = version_match.group(1)

        assert expected_version in result.output, (
            f"CLI version output '{result.output}' does not contain expected version '{expected_version}'"
        )

    def test_version_format(self):
        """Version string follows semantic versioning format."""
        import bpsai_pair

        # Semantic versioning pattern: MAJOR.MINOR.PATCH with optional prerelease
        semver_pattern = re.compile(
            r"^[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
        )

        assert semver_pattern.match(bpsai_pair.__version__), (
            f"Version '{bpsai_pair.__version__}' does not follow semantic versioning"
        )
