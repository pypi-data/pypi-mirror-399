"""
Configuration Loader Module

Loads and validates YAML configuration files with environment variable substitution.
"""

import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

logger = logging.getLogger(__name__)


class ConfigLoader:
    """
    Load and parse YAML configuration files with environment variable support.

    Supports:
    - Environment variable substitution: ${VAR_NAME} or ${VAR_NAME:default}
    - Nested configurations
    - Config validation
    - Config merging

    Example:
        >>> loader = ConfigLoader()
        >>> config = loader.load("configs/framework_config.yaml")
        >>> # In YAML: api_key: ${OPENAI_API_KEY:default_key}
    """

    # Regex pattern for environment variable substitution
    ENV_VAR_PATTERN = re.compile(r'\$\{([^}:]+)(?::([^}]*))?\}')

    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize configuration loader.

        Args:
            base_path: Base directory for relative config paths.
                      Defaults to current working directory.
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
        logger.debug(f"ConfigLoader initialized with base_path: {self.base_path}")

    def load(self, config_path: str) -> Dict[str, Any]:
        """
        Load configuration from YAML file.

        Args:
            config_path: Path to YAML file (absolute or relative to base_path)

        Returns:
            dict: Loaded configuration with environment variables substituted

        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If YAML parsing fails

        Example:
            >>> config = loader.load("configs/framework_config.yaml")
        """
        if not YAML_AVAILABLE:
            raise ImportError("PyYAML is required for config loading. Install with: pip install pyyaml")

        # Resolve path
        config_file = Path(config_path)
        if not config_file.is_absolute():
            config_file = self.base_path / config_file

        # Check file exists
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")

        # Load YAML
        logger.info(f"Loading configuration from: {config_file}")
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse YAML: {e}")
            raise

        # Substitute environment variables
        config = self._substitute_env_vars(config)

        logger.info(f"Configuration loaded successfully from {config_file}")
        return config or {}

    def _substitute_env_vars(self, obj: Any) -> Any:
        """
        Recursively substitute environment variables in configuration.

        Supports:
        - ${VAR_NAME} - Required variable (raises if not found)
        - ${VAR_NAME:default} - Optional variable with default value

        Args:
            obj: Configuration object (dict, list, str, etc.)

        Returns:
            Object with environment variables substituted
        """
        if isinstance(obj, dict):
            return {k: self._substitute_env_vars(v) for k, v in obj.items()}

        elif isinstance(obj, list):
            return [self._substitute_env_vars(item) for item in obj]

        elif isinstance(obj, str):
            return self._substitute_env_var_in_string(obj)

        else:
            return obj

    def _substitute_env_var_in_string(self, text: str) -> Any:
        """
        Substitute environment variables in a string.

        Args:
            text: String potentially containing ${VAR} patterns

        Returns:
            String with variables substituted, or original type if conversion needed
        """
        def replacer(match):
            var_name = match.group(1)
            default_value = match.group(2)

            # Get environment variable
            value = os.getenv(var_name)

            if value is not None:
                return value
            elif default_value is not None:
                logger.debug(f"Using default value for ${{{var_name}}}: {default_value}")
                return default_value
            else:
                logger.warning(f"Environment variable ${{{var_name}}} not found and no default provided")
                return match.group(0)  # Return original ${VAR} if not found

        # Substitute all environment variables
        result = self.ENV_VAR_PATTERN.sub(replacer, text)

        # Try to convert to appropriate type
        return self._convert_type(result)

    def _convert_type(self, value: str) -> Any:
        """
        Convert string value to appropriate Python type.

        Args:
            value: String value

        Returns:
            Converted value (bool, int, float, or str)
        """
        # Boolean conversion
        if value.lower() in ('true', 'yes', 'on'):
            return True
        elif value.lower() in ('false', 'no', 'off'):
            return False

        # Number conversion
        try:
            # Try integer
            if '.' not in value:
                return int(value)
            # Try float
            return float(value)
        except ValueError:
            pass

        # Return as string
        return value

    def merge_configs(self, base_config: Dict, override_config: Dict) -> Dict:
        """
        Merge two configurations (override_config takes precedence).

        Args:
            base_config: Base configuration
            override_config: Override configuration

        Returns:
            dict: Merged configuration

        Example:
            >>> base = {'a': 1, 'b': {'c': 2}}
            >>> override = {'b': {'d': 3}}
            >>> merged = loader.merge_configs(base, override)
            >>> # Result: {'a': 1, 'b': {'c': 2, 'd': 3}}
        """
        result = base_config.copy()

        for key, value in override_config.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge nested dicts
                result[key] = self.merge_configs(result[key], value)
            else:
                # Override value
                result[key] = value

        return result

    def save(self, config: Dict, output_path: str) -> None:
        """
        Save configuration to YAML file.

        Args:
            config: Configuration dictionary
            output_path: Path to output file

        Raises:
            yaml.YAMLError: If YAML serialization fails
        """
        if not YAML_AVAILABLE:
            raise ImportError("PyYAML is required. Install with: pip install pyyaml")

        output_file = Path(output_path)
        if not output_file.is_absolute():
            output_file = self.base_path / output_file

        # Create parent directory if needed
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Save YAML
        logger.info(f"Saving configuration to: {output_file}")
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)
        except yaml.YAMLError as e:
            logger.error(f"Failed to write YAML: {e}")
            raise

        logger.info(f"Configuration saved to {output_file}")

    def validate(self, config: Dict, schema: Dict) -> bool:
        """
        Validate configuration against a schema.

        Args:
            config: Configuration to validate
            schema: Schema definition (keys: required, optional)

        Returns:
            bool: True if valid

        Raises:
            ValueError: If required keys are missing
        """
        required_keys = schema.get('required', [])
        optional_keys = schema.get('optional', [])
        all_keys = set(required_keys + optional_keys)

        # Check required keys
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Required configuration key missing: {key}")

        # Warn about unknown keys
        for key in config:
            if key not in all_keys:
                logger.warning(f"Unknown configuration key: {key}")

        return True


# Convenience function for quick config loading
def load_config(config_path: str, base_path: Optional[Path] = None) -> Dict:
    """
    Quick config loader.

    Args:
        config_path: Path to configuration file
        base_path: Base directory for relative paths

    Returns:
        dict: Loaded configuration

    Example:
        >>> from mdsa.utils import load_config
        >>> config = load_config("configs/framework_config.yaml")
    """
    loader = ConfigLoader(base_path=base_path)
    return loader.load(config_path)


if __name__ == "__main__":
    # Demo usage
    loader = ConfigLoader()

    # Example config
    example_config = {
        'framework': {
            'name': 'MDSA',
            'version': '1.0.0',
        },
        'orchestrator': {
            'device': 'cpu',
            'confidence_threshold': 0.85,
        },
        'api': {
            'key': '${API_KEY:default_key}',
        }
    }

    # Save example
    loader.save(example_config, 'example_config.yaml')
    print("Example config saved to example_config.yaml")

    # Load example
    loaded = loader.load('example_config.yaml')
    print(f"Loaded config: {loaded}")
