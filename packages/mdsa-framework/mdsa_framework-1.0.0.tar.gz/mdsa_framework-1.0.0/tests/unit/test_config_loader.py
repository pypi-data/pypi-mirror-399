"""
Unit tests for Configuration Loader module.

Tests YAML loading, environment variable substitution, and config merging.
"""

import os
import tempfile
import unittest
from pathlib import Path
from mdsa.utils.config_loader import ConfigLoader, load_config


class TestConfigLoader(unittest.TestCase):
    """Test suite for ConfigLoader class."""

    def setUp(self):
        """Set up test fixtures."""
        self.loader = ConfigLoader()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_temp_config(self, content: str) -> str:
        """Helper to create temporary config file."""
        config_path = os.path.join(self.temp_dir, "test_config.yaml")
        with open(config_path, 'w') as f:
            f.write(content)
        return config_path

    def test_initialization(self):
        """Test ConfigLoader initialization."""
        self.assertIsNotNone(self.loader)

    def test_load_simple_yaml(self):
        """Test loading simple YAML configuration."""
        content = """
        framework:
          name: "MDSA"
          version: "1.0.0"
        """
        config_path = self._create_temp_config(content)
        config = self.loader.load(config_path)

        self.assertIsInstance(config, dict)
        self.assertIn('framework', config)
        self.assertEqual(config['framework']['name'], "MDSA")
        self.assertEqual(config['framework']['version'], "1.0.0")

    def test_load_nested_yaml(self):
        """Test loading nested YAML configuration."""
        content = """
        orchestrator:
          confidence_threshold: 0.85
          router:
            model_name: "tinybert"
            device: "cpu"
        """
        config_path = self._create_temp_config(content)
        config = self.loader.load(config_path)

        self.assertEqual(config['orchestrator']['confidence_threshold'], 0.85)
        self.assertEqual(config['orchestrator']['router']['device'], "cpu")

    def test_env_var_substitution_simple(self):
        """Test simple environment variable substitution."""
        os.environ['TEST_VAR'] = 'test_value'
        content = """
        test_key: "${TEST_VAR}"
        """
        config_path = self._create_temp_config(content)
        config = self.loader.load(config_path)

        self.assertEqual(config['test_key'], 'test_value')
        del os.environ['TEST_VAR']

    def test_env_var_substitution_with_default(self):
        """Test environment variable substitution with default value."""
        content = """
        test_key: "${NONEXISTENT_VAR:default_value}"
        """
        config_path = self._create_temp_config(content)
        config = self.loader.load(config_path)

        self.assertEqual(config['test_key'], 'default_value')

    def test_env_var_substitution_nested(self):
        """Test environment variable substitution in nested values."""
        os.environ['TEST_PORT'] = '8080'
        content = """
        server:
          host: "localhost"
          port: "${TEST_PORT}"
        """
        config_path = self._create_temp_config(content)
        config = self.loader.load(config_path)

        self.assertEqual(config['server']['port'], '8080')
        del os.environ['TEST_PORT']

    def test_home_directory_expansion(self):
        """Test ~ expansion to home directory."""
        content = """
        cache_dir: "~/.mdsa/cache"
        """
        config_path = self._create_temp_config(content)
        config = self.loader.load(config_path)

        self.assertIn(str(Path.home()), config['cache_dir'])
        self.assertNotIn('~', config['cache_dir'])

    def test_multiple_env_vars_in_value(self):
        """Test multiple environment variables in single value."""
        os.environ['TEST_HOST'] = 'localhost'
        os.environ['TEST_PORT'] = '8080'
        content = """
        url: "http://${TEST_HOST}:${TEST_PORT}/api"
        """
        config_path = self._create_temp_config(content)
        config = self.loader.load(config_path)

        self.assertEqual(config['url'], 'http://localhost:8080/api')
        del os.environ['TEST_HOST']
        del os.environ['TEST_PORT']

    def test_load_nonexistent_file(self):
        """Test loading non-existent file raises error."""
        with self.assertRaises(FileNotFoundError):
            self.loader.load("/nonexistent/path/config.yaml")

    def test_load_invalid_yaml(self):
        """Test loading invalid YAML raises error."""
        content = """
        invalid: yaml: content:
          - broken
        """
        config_path = self._create_temp_config(content)
        with self.assertRaises(Exception):
            self.loader.load(config_path)

    def test_get_nested_value(self):
        """Test getting nested configuration values."""
        content = """
        level1:
          level2:
            level3: "deep_value"
        """
        config_path = self._create_temp_config(content)
        config = self.loader.load(config_path)

        value = self.loader.get(config, "level1.level2.level3")
        self.assertEqual(value, "deep_value")

    def test_get_nested_value_with_default(self):
        """Test getting nested value with default."""
        config = {'level1': {'level2': 'value'}}
        value = self.loader.get(config, "level1.nonexistent", default="default")
        self.assertEqual(value, "default")

    def test_merge_configs(self):
        """Test merging multiple configurations."""
        base_config = {'a': 1, 'b': {'c': 2}}
        override_config = {'b': {'c': 3, 'd': 4}, 'e': 5}

        merged = self.loader.merge(base_config, override_config)

        self.assertEqual(merged['a'], 1)
        self.assertEqual(merged['b']['c'], 3)
        self.assertEqual(merged['b']['d'], 4)
        self.assertEqual(merged['e'], 5)

    def test_validate_config_structure(self):
        """Test configuration validation."""
        content = """
        framework:
          name: "MDSA"
        orchestrator:
          confidence_threshold: 0.85
        """
        config_path = self._create_temp_config(content)
        config = self.loader.load(config_path)

        # Should have required keys
        self.assertIn('framework', config)
        self.assertIn('orchestrator', config)


class TestLoadConfigConvenience(unittest.TestCase):
    """Test suite for load_config convenience function."""

    def test_load_config_function(self):
        """Test load_config convenience function."""
        # Create temporary config
        temp_dir = tempfile.mkdtemp()
        config_path = os.path.join(temp_dir, "test.yaml")

        with open(config_path, 'w') as f:
            f.write("test_key: test_value\n")

        config = load_config(config_path)
        self.assertIsInstance(config, dict)
        self.assertEqual(config['test_key'], 'test_value')

        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)


if __name__ == '__main__':
    unittest.main()
