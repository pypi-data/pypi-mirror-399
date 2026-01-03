"""Tests for the core/ module structure (T24.1)."""

import pytest


class TestCoreModuleStructure:
    """Test that core/ module exists and can be imported."""

    def test_core_module_imports(self):
        """Core module can be imported."""
        from bpsai_pair import core
        assert core is not None

    def test_core_config_imports(self):
        """core/config.py can be imported."""
        from bpsai_pair.core import config
        assert config is not None

    def test_core_constants_imports(self):
        """core/constants.py can be imported."""
        from bpsai_pair.core import constants
        assert constants is not None

    def test_core_hooks_imports(self):
        """core/hooks.py can be imported."""
        from bpsai_pair.core import hooks
        assert hooks is not None

    def test_core_ops_imports(self):
        """core/ops.py can be imported."""
        from bpsai_pair.core import ops
        assert ops is not None

    def test_core_presets_imports(self):
        """core/presets.py can be imported."""
        from bpsai_pair.core import presets
        assert presets is not None

    def test_core_utils_imports(self):
        """core/utils.py can be imported."""
        from bpsai_pair.core import utils
        assert utils is not None

    def test_core_init_exports_modules(self):
        """core/__init__.py exports all submodules."""
        from bpsai_pair.core import (
            config,
            constants,
            hooks,
            ops,
            presets,
            utils,
        )
        # All should be importable
        assert all([config, constants, hooks, ops, presets, utils])
