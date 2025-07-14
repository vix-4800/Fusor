from fusor import config

def test_save_then_load(tmp_path, monkeypatch):
    cfg_file = tmp_path / "config.json"
    monkeypatch.setattr(config, "CONFIG_FILE", str(cfg_file))
    data = {
        "foo": 123,
        "bar": [1, 2, 3],
        "use_docker": True,
        "php_service": "php",
        "server_port": 9000,
    }
    config.save_config(data)
    loaded = config.load_config()
    assert loaded == data

def test_load_missing_file(tmp_path, monkeypatch):
    cfg_file = tmp_path / "missing.json"
    monkeypatch.setattr(config, "CONFIG_FILE", str(cfg_file))
    assert config.load_config() == {
        "use_docker": False,
        "php_service": "php",
        "server_port": 8000,
    }

def test_load_invalid_json(tmp_path, monkeypatch):
    cfg_file = tmp_path / "broken.json"
    cfg_file.write_text("{ invalid json")
    monkeypatch.setattr(config, "CONFIG_FILE", str(cfg_file))
    assert config.load_config() == {
        "use_docker": False,
        "php_service": "php",
        "server_port": 8000,
    }
