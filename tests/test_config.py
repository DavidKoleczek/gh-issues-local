"""Tests for gh_issues_local.config."""

from pathlib import Path

from gh_issues_local.config import Config, load_config
import pytest
import yaml


class TestLoadConfigDefaults:
    """When no CONFIG_FILE is set, load_config returns defaults."""

    def test_returns_config_instance(self, monkeypatch):
        monkeypatch.delenv("CONFIG_FILE", raising=False)
        monkeypatch.delenv("GH_ISSUES_LOCAL_DATA_DIR", raising=False)
        config = load_config()
        assert isinstance(config, Config)

    def test_default_data_dir_is_home(self, monkeypatch):
        monkeypatch.delenv("CONFIG_FILE", raising=False)
        monkeypatch.delenv("GH_ISSUES_LOCAL_DATA_DIR", raising=False)
        config = load_config()
        assert config.data_dir == Path.home()

    def test_default_storage_is_none(self, monkeypatch):
        monkeypatch.delenv("CONFIG_FILE", raising=False)
        config = load_config()
        assert config.storage is None

    def test_default_auth_token_is_none(self, monkeypatch):
        monkeypatch.delenv("CONFIG_FILE", raising=False)
        config = load_config()
        assert config.auth_token is None


class TestLoadConfigFromYaml:
    """When CONFIG_FILE points to a YAML file, values are loaded."""

    def test_loads_storage_from_yaml(self, monkeypatch, tmp_path):
        config_file = tmp_path / "service.yaml"
        config_file.write_text(
            yaml.dump(
                {
                    "storage": {"provider": "local", "local": {"root_path": "./storage"}},
                }
            )
        )
        monkeypatch.setenv("CONFIG_FILE", str(config_file))
        monkeypatch.delenv("GH_ISSUES_LOCAL_DATA_DIR", raising=False)
        config = load_config()
        assert config.storage == {"provider": "local", "local": {"root_path": "./storage"}}

    def test_loads_auth_token_from_yaml(self, monkeypatch, tmp_path):
        config_file = tmp_path / "service.yaml"
        config_file.write_text(yaml.dump({"auth": {"token": "secret123"}}))
        monkeypatch.setenv("CONFIG_FILE", str(config_file))
        monkeypatch.delenv("GH_ISSUES_LOCAL_DATA_DIR", raising=False)
        config = load_config()
        assert config.auth_token == "secret123"

    def test_null_auth_token_in_yaml_gives_none(self, monkeypatch, tmp_path):
        config_file = tmp_path / "service.yaml"
        config_file.write_text(yaml.dump({"auth": {"token": None}}))
        monkeypatch.setenv("CONFIG_FILE", str(config_file))
        monkeypatch.delenv("GH_ISSUES_LOCAL_DATA_DIR", raising=False)
        config = load_config()
        assert config.auth_token is None


class TestLoadConfigEnvOverrides:
    """Env vars override YAML values."""

    def test_data_dir_env_overrides_default(self, monkeypatch, tmp_path):
        monkeypatch.delenv("CONFIG_FILE", raising=False)
        monkeypatch.setenv("GH_ISSUES_LOCAL_DATA_DIR", str(tmp_path))
        config = load_config()
        assert config.data_dir == tmp_path

    def test_data_dir_env_overrides_yaml(self, monkeypatch, tmp_path):
        config_file = tmp_path / "service.yaml"
        config_file.write_text(yaml.dump({"storage": {"provider": "local"}}))
        monkeypatch.setenv("CONFIG_FILE", str(config_file))
        override_dir = tmp_path / "override"
        override_dir.mkdir()
        monkeypatch.setenv("GH_ISSUES_LOCAL_DATA_DIR", str(override_dir))
        config = load_config()
        assert config.data_dir == override_dir


class TestLoadConfigErrorHandling:
    """Error handling for bad config files."""

    def test_missing_config_file_logs_warning_and_uses_defaults(self, monkeypatch, tmp_path):
        monkeypatch.setenv("CONFIG_FILE", str(tmp_path / "nonexistent.yaml"))
        monkeypatch.delenv("GH_ISSUES_LOCAL_DATA_DIR", raising=False)
        # Should not raise -- falls back to defaults.
        config = load_config()
        assert isinstance(config, Config)
        assert config.storage is None

    def test_malformed_yaml_raises(self, monkeypatch, tmp_path):
        config_file = tmp_path / "bad.yaml"
        config_file.write_text(": : : not valid yaml [[[")
        monkeypatch.setenv("CONFIG_FILE", str(config_file))
        with pytest.raises(ValueError, match=r"bad.yaml"):
            load_config()
