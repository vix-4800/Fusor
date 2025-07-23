from fusor import config
from fusor.config import DEFAULT_CONFIG

def test_save_then_load(tmp_path, monkeypatch):
    cfg_file = tmp_path / "config.json"
    monkeypatch.setattr(config, "CONFIG_FILE", str(cfg_file))
    data = {
        "foo": 123,
        "bar": [1, 2, 3],
        "projects": [
            {"path": "/one", "name": "one"},
            {
                "path": "/two",
                "name": "two",
                "use_docker": True,
                "php_service": "php",
                "server_port": 9000,
                "yii_template": "advanced",
                "log_dirs": ["/tmp/logs"],
                "git_remote": "origin",
                "compose_files": ["dc.yml"],
                "auto_refresh_secs": 7,
                "enable_terminal": False,
            },
        ],
        "current_project": "/two",
        "theme": "light",
        "window_size": [800, 600],
        "window_position": [10, 20],
    }
    config.save_config(data)
    loaded = config.load_config()
    data.setdefault("show_console_output", False)
    data.setdefault("enable_tray", False)
    assert loaded == data

def test_load_missing_file(tmp_path, monkeypatch):
    cfg_file = tmp_path / "missing.json"
    monkeypatch.setattr(config, "CONFIG_FILE", str(cfg_file))
    assert config.load_config() == DEFAULT_CONFIG

def test_load_invalid_json(tmp_path, monkeypatch):
    cfg_file = tmp_path / "broken.json"
    cfg_file.write_text("{ invalid json")
    monkeypatch.setattr(config, "CONFIG_FILE", str(cfg_file))
    assert config.load_config() == DEFAULT_CONFIG


def test_load_returns_copy(tmp_path, monkeypatch):
    """Modifying the loaded config should not affect DEFAULT_CONFIG."""
    cfg_file = tmp_path / "missing.json"
    monkeypatch.setattr(config, "CONFIG_FILE", str(cfg_file))
    loaded = config.load_config()
    loaded["projects"].append({"path": "/foo", "name": "foo"})
    loaded["window_size"][0] = 500
    assert DEFAULT_CONFIG["projects"] == []
    assert DEFAULT_CONFIG["window_size"] == [1024, 768]
