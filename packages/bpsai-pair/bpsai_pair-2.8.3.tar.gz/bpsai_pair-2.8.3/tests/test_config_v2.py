"""Tests for v2 config contract (Task 1).

Ensures `.paircoder/config.yaml` is the canonical config file produced by init/config tooling,
and that generated templates reference the correct path.
"""

from pathlib import Path

import yaml

from bpsai_pair.core.config import Config, ContextTemplate


def test_save_v2_creates_paircoder_config_yaml(tmp_path: Path):
    cfg = Config()
    path = cfg.save(tmp_path, use_v2=True)

    assert path == tmp_path / ".paircoder" / "config.yaml"
    assert path.exists()

    data = yaml.safe_load(path.read_text()) or {}
    assert data.get("version") == "2"


def test_ensure_v2_config_writes_config_if_missing(tmp_path: Path):
    from bpsai_pair.commands.core import ensure_v2_config

    path = ensure_v2_config(tmp_path)
    assert path == tmp_path / ".paircoder" / "config.yaml"
    assert path.exists()


def test_agents_template_references_v2_config_path():
    md = ContextTemplate.agents_md(Config())
    # Template shows .paircoder/ directory with config.yaml inside
    assert ".paircoder/" in md
    assert "config.yaml" in md
    assert ".paircoder.yml" not in md
