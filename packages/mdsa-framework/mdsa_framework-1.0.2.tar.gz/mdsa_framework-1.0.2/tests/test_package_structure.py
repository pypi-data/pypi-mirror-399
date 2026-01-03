"""
Test Package Structure

Verifies that all modules can be imported successfully.
"""

import pytest


class TestPackageStructure:
    """Test that all package modules can be imported."""

    def test_import_mdsa_main(self):
        """Test that main mdsa package can be imported."""
        import mdsa

        assert hasattr(mdsa, "__version__")
        assert mdsa.__version__ == "1.0.0"
        assert hasattr(mdsa, "MDSA")

    def test_import_core_module(self):
        """Test that mdsa.core module can be imported."""
        import mdsa.core

        assert mdsa.core is not None

    def test_import_domains_module(self):
        """Test that mdsa.domains module can be imported."""
        import mdsa.domains

        assert mdsa.domains is not None

    def test_import_models_module(self):
        """Test that mdsa.models module can be imported."""
        import mdsa.models

        assert mdsa.models is not None

    def test_import_rag_module(self):
        """Test that mdsa.rag module can be imported."""
        import mdsa.rag

        assert mdsa.rag is not None

    def test_import_communication_module(self):
        """Test that mdsa.communication module can be imported."""
        import mdsa.communication

        assert mdsa.communication is not None

    def test_import_validation_module(self):
        """Test that mdsa.validation module can be imported."""
        import mdsa.validation

        assert mdsa.validation is not None

    def test_import_integrations_module(self):
        """Test that mdsa.integrations module can be imported."""
        import mdsa.integrations

        assert mdsa.integrations is not None

    def test_import_monitoring_module(self):
        """Test that mdsa.monitoring module can be imported."""
        import mdsa.monitoring

        assert mdsa.monitoring is not None

    def test_import_ui_module(self):
        """Test that mdsa.ui module can be imported."""
        import mdsa.ui

        assert mdsa.ui is not None

    def test_import_utils_module(self):
        """Test that mdsa.utils module can be imported."""
        import mdsa.utils

        assert mdsa.utils is not None

    def test_mdsa_class_instantiation(self):
        """Test that MDSA class can be instantiated."""
        from mdsa import MDSA

        mdsa_instance = MDSA()
        assert mdsa_instance is not None
        assert mdsa_instance.version == "1.0.0"

    def test_mdsa_class_with_config(self):
        """Test that MDSA class can be instantiated with config path."""
        from mdsa import MDSA

        mdsa_instance = MDSA(config_path="test_config.yaml")
        assert mdsa_instance is not None
        assert mdsa_instance.config_path == "test_config.yaml"


class TestModuleAttributes:
    """Test that modules have expected attributes."""

    def test_mdsa_main_attributes(self):
        """Test main mdsa module attributes."""
        import mdsa

        assert hasattr(mdsa, "__version__")
        assert hasattr(mdsa, "__author__")
        assert hasattr(mdsa, "__license__")
        assert mdsa.__license__ == "Apache 2.0"

    def test_mdsa_all_exports(self):
        """Test that __all__ is defined."""
        import mdsa

        assert hasattr(mdsa, "__all__")
        assert isinstance(mdsa.__all__, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
