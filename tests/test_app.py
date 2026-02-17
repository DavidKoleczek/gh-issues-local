"""Tests for gh_issues_local.app -- config-driven storage setup."""


import yaml

from gh_issues_local.config import Config


class TestEnsureStorageConfig:
    """_ensure_storage_config writes config files based on Config.storage."""

    def test_no_config_storage_writes_hardcoded_defaults(self, monkeypatch, tmp_path):
        """When config.storage is None, write the same defaults as before."""
        monkeypatch.setenv("GH_ISSUES_LOCAL_DATA_DIR", str(tmp_path))
        config = Config(data_dir=tmp_path, storage=None)

        from gh_issues_local.app import _ensure_storage_config

        _ensure_storage_config(config)

        storage_yaml = tmp_path / ".storage.yaml"
        assert storage_yaml.read_text() == "provider: local\n"
        local_yaml = tmp_path / ".local_storage.yaml"
        assert local_yaml.read_text() == "root_path: ./storage\n"

    def test_config_storage_writes_yaml_values(self, monkeypatch, tmp_path):
        """When config.storage has values, write those instead of defaults."""
        monkeypatch.setenv("GH_ISSUES_LOCAL_DATA_DIR", str(tmp_path))
        storage = {"provider": "local", "local": {"root_path": "/data/storage"}}
        config = Config(data_dir=tmp_path, storage=storage)

        from gh_issues_local.app import _ensure_storage_config

        _ensure_storage_config(config)

        storage_yaml = tmp_path / ".storage.yaml"
        assert yaml.safe_load(storage_yaml.read_text()) == {"provider": "local"}
        local_yaml = tmp_path / ".local_storage.yaml"
        assert yaml.safe_load(local_yaml.read_text()) == {"root_path": "/data/storage"}

    def test_existing_storage_yaml_is_not_overwritten(self, monkeypatch, tmp_path):
        """If .storage.yaml already exists, don't touch it."""
        monkeypatch.setenv("GH_ISSUES_LOCAL_DATA_DIR", str(tmp_path))
        existing = tmp_path / ".storage.yaml"
        existing.write_text("provider: git\n")
        config = Config(data_dir=tmp_path, storage={"provider": "local"})

        from gh_issues_local.app import _ensure_storage_config

        _ensure_storage_config(config)

        assert existing.read_text() == "provider: git\n"
