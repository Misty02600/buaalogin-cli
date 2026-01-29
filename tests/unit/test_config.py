"""config 模块单元测试"""

import pytest
from msgspec import UNSET, DecodeError

from buaalogin_cli.config import Config


class TestConfigStruct:
    """测试 Config 结构体"""

    def test_config_default_values(self):
        """测试 Config 默认值为 UNSET"""
        config = Config()
        assert config.username is UNSET
        assert config.password is UNSET
        assert config.interval is UNSET

    def test_config_with_values(self):
        """测试带参数创建 Config"""
        config = Config(username="test", password="pass", interval=10)
        assert config.username == "test"
        assert config.password == "pass"
        assert config.interval == 10

    def test_config_partial_values(self):
        """测试部分参数创建 Config"""
        config = Config(username="user")
        assert config.username == "user"
        assert config.password is UNSET
        assert config.interval is UNSET


class TestConfigToDict:
    """测试 Config.to_dict 方法"""

    def test_to_dict_empty(self):
        """测试空 Config 转换为空字典"""
        config = Config()
        result = config.to_dict()
        assert result == {}

    def test_to_dict_with_values(self):
        """测试带值 Config 转换为字典"""
        config = Config(username="test", password="pass", interval=5)
        result = config.to_dict()
        assert result == {"username": "test", "password": "pass", "interval": 5}

    def test_to_dict_partial(self):
        """测试部分值 Config 转换为字典（过滤 UNSET）"""
        config = Config(username="test")
        result = config.to_dict()
        assert result == {"username": "test"}
        assert "password" not in result
        assert "interval" not in result


class TestConfigLoadFromJson:
    """测试 Config.load_from_json 方法"""

    def test_load_valid_config(self, temp_config_file):
        """测试加载有效配置文件"""
        config = Config.load_from_json(temp_config_file)
        assert config.username == "test_user"
        assert config.password == "test_pass"
        assert config.interval == 5

    def test_load_empty_config(self, empty_config_file):
        """测试加载空配置文件"""
        config = Config.load_from_json(empty_config_file)
        assert config.username is UNSET
        assert config.password is UNSET
        assert config.interval is UNSET

    def test_load_partial_config(self, tmp_path):
        """测试加载部分配置"""
        config_file = tmp_path / "partial.json"
        config_file.write_text('{"username": "only_user"}')
        config = Config.load_from_json(config_file)
        assert config.username == "only_user"
        assert config.password is UNSET

    def test_load_nonexistent_file(self, tmp_path):
        """测试加载不存在的文件返回空配置"""
        config = Config.load_from_json(tmp_path / "nonexistent.json")
        assert config.username is UNSET
        assert config.password is UNSET
        assert config.interval is UNSET

    def test_load_invalid_json(self, tmp_path):
        """测试加载无效 JSON 抛出异常"""
        config_file = tmp_path / "invalid.json"
        config_file.write_text("not valid json")
        with pytest.raises(DecodeError):
            Config.load_from_json(config_file)


class TestConfigSaveToJson:
    """测试 Config.save_to_json 方法"""

    def test_save_and_load(self, tmp_path):
        """测试保存后重新加载"""
        config_file = tmp_path / "save_test.json"
        original = Config(username="save_user", password="save_pass", interval=15)
        original.save_to_json(config_file)

        loaded = Config.load_from_json(config_file)
        assert loaded.username == "save_user"
        assert loaded.password == "save_pass"
        assert loaded.interval == 15

    def test_save_empty_config(self, tmp_path):
        """测试保存空配置"""
        config_file = tmp_path / "empty.json"
        config = Config()
        config.save_to_json(config_file)

        content = config_file.read_text()
        assert content.strip() == "{}"

    def test_save_partial_config(self, tmp_path):
        """测试保存部分配置（omit_defaults 生效）"""
        config_file = tmp_path / "partial.json"
        config = Config(username="only")
        config.save_to_json(config_file)

        content = config_file.read_text()
        assert "only" in content
        assert "password" not in content
