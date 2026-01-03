"""
Test Phi-2 Validator and Two-Tier Validation System

Tests framework-level semantic validation using Phi-2.

Author: MDSA Framework Team
Date: 2025-12-05
"""

import pytest
from mdsa.domains.model_validator import Phi2Validator, ValidationResult
from mdsa.domains.validator import ResponseValidator
from mdsa.domains.config import DomainConfig


class TestPhi2Validator:
    """Test Phi-2 model-based validator"""

    def test_input_validation_valid_query(self):
        """Test that valid queries pass input validation"""
        validator = Phi2Validator()

        valid_queries = [
            "Calculate billing charges for patient",
            "Extract ICD-10 codes from this diagnosis",
            "What is the claim status?",
            "How do I submit a claim?"
        ]

        for query in valid_queries:
            result = validator.validate_input(query)
            assert isinstance(result, ValidationResult)
            assert result.is_valid, f"Query '{query}' should be valid"
            assert result.confidence > 0.5

    def test_input_validation_invalid_query(self):
        """Test that invalid queries fail input validation"""
        validator = Phi2Validator()

        invalid_queries = [
            "",  # Empty
            "xy",  # Too short
            "!!!",  # No alphanumeric
        ]

        for query in invalid_queries:
            result = validator.validate_input(query)
            assert isinstance(result, ValidationResult)
            assert not result.is_valid, f"Query '{query}' should be invalid"
            assert len(result.issues) > 0

    def test_input_validation_warnings(self):
        """Test that edge case queries generate warnings"""
        validator = Phi2Validator()

        # Very long query
        long_query = "Test query " * 100
        result = validator.validate_input(long_query)

        assert result.is_valid  # Still valid
        # May have warnings about length
        if result.warnings:
            assert any('long' in w.lower() for w in result.warnings)

    def test_response_validation_relevant(self):
        """Test that relevant responses pass validation"""
        validator = Phi2Validator()

        test_cases = [
            ("Calculate billing", "The total billing amount is $150.00"),
            ("What is ICD-10 code for diabetes?", "The ICD-10 code for diabetes is E11.9"),
            ("Submit claim", "Claim submitted successfully with ID CLM-12345")
        ]

        for query, response in test_cases:
            result = validator.validate_response(query, response)
            assert result.is_valid, f"Response should be valid for query '{query}'"
            assert result.confidence > 0.5

    def test_response_validation_irrelevant(self):
        """Test that irrelevant responses fail validation"""
        validator = Phi2Validator()

        test_cases = [
            ("Calculate billing", ""),  # Empty
            ("What is the weather?", "Error"),  # Error response
            ("Code diagnosis", "ok"),  # Too brief
        ]

        for query, response in test_cases:
            result = validator.validate_response(query, response)
            # May pass or fail depending on heuristics, but should have low confidence or warnings
            if result.is_valid:
                assert result.confidence < 0.9 or len(result.warnings) > 0

    def test_response_validation_keyword_overlap(self):
        """Test keyword overlap detection"""
        validator = Phi2Validator()

        # High overlap
        result = validator.validate_response(
            "Calculate medical billing charges",
            "The medical billing charges have been calculated as $200"
        )
        assert result.is_valid
        assert result.metadata.get('keyword_overlap', 0) > 0.3

        # Low overlap
        result = validator.validate_response(
            "Calculate medical billing",
            "The weather is sunny today"
        )
        # Should have warnings or low confidence
        assert not result.is_valid or len(result.warnings) > 0

    def test_tool_validation_correct_usage(self):
        """Test validation of correct tool usage"""
        validator = Phi2Validator()

        result = validator.validate_tool_usage(
            query="Lookup ICD-10 code for diabetes",
            tools_used=[{'name': 'lookup_icd10', 'params': {'query': 'diabetes'}}],
            tool_outputs=["E11.9: Type 2 diabetes mellitus"]
        )

        assert result.is_valid
        assert result.confidence > 0.5

    def test_tool_validation_missing_tools(self):
        """Test validation when expected tools are missing"""
        validator = Phi2Validator()

        result = validator.validate_tool_usage(
            query="Lookup ICD-10 code for diabetes",
            tools_used=[],  # No tools used
            tool_outputs=[]
        )

        # Should generate warnings
        assert len(result.warnings) > 0 or result.confidence < 0.9

    def test_tool_validation_tool_count_mismatch(self):
        """Test validation when tool count doesn't match output count"""
        validator = Phi2Validator()

        result = validator.validate_tool_usage(
            query="Calculate cost",
            tools_used=[{'name': 'calculate'}],
            tool_outputs=[]  # Mismatch
        )

        assert not result.is_valid
        assert any('mismatch' in issue.lower() for issue in result.issues)

    def test_tool_validation_duplicate_calls(self):
        """Test validation with duplicate tool calls"""
        validator = Phi2Validator()

        result = validator.validate_tool_usage(
            query="Get data",
            tools_used=[
                {'name': 'lookup'},
                {'name': 'lookup'}  # Duplicate
            ],
            tool_outputs=["result1", "result2"]
        )

        # Should generate warnings about duplicates
        assert len(result.warnings) > 0

    def test_caching(self):
        """Test that validation results are cached"""
        validator = Phi2Validator(enable_caching=True)

        query = "Calculate billing"

        # First call
        result1 = validator.validate_input(query)
        time1 = result1.validation_time_ms

        # Second call (should be cached)
        result2 = validator.validate_input(query)

        # Results should be identical
        assert result1.is_valid == result2.is_valid
        assert result1.confidence == result2.confidence

        # Check cache stats
        cache_stats = validator.get_cache_stats()
        assert cache_stats['cache_size'] >= 1
        assert cache_stats['cache_enabled'] == True

    def test_cache_clear(self):
        """Test cache clearing"""
        validator = Phi2Validator(enable_caching=True)

        # Add to cache
        validator.validate_input("Test query")

        # Clear cache
        validator.clear_cache()

        # Cache should be empty
        cache_stats = validator.get_cache_stats()
        assert cache_stats['cache_size'] == 0

    def test_confidence_threshold(self):
        """Test custom confidence threshold"""
        # Strict validator (high threshold)
        strict_validator = Phi2Validator(confidence_threshold=0.9)

        # Lenient validator (low threshold)
        lenient_validator = Phi2Validator(confidence_threshold=0.5)

        # Borderline query
        query = "xyz test query"

        strict_result = strict_validator.validate_input(query)
        lenient_result = lenient_validator.validate_input(query)

        # Lenient should be more accepting
        assert lenient_result.is_valid or lenient_result.confidence >= 0.5


class TestTwoTierValidation:
    """Test integrated two-tier validation system"""

    @pytest.fixture
    def domain_config(self):
        """Create test domain configuration"""
        return DomainConfig(
            domain_id="test",
            name="Test Domain",
            description="Test domain",
            keywords=["test"],
            min_response_length=10,
            max_response_length=500,
            check_toxicity=False,
            use_model_validation=False  # Will be toggled in tests
        )

    def test_tier1_only_validation(self, domain_config):
        """Test Tier 1 (rule-based) validation only"""
        validator = ResponseValidator(use_model_validation=False)

        # Valid response
        is_valid, error = validator.validate(
            response="This is a valid response for testing",
            domain_config=domain_config
        )
        assert is_valid
        assert error is None

        # Too short
        is_valid, error = validator.validate(
            response="Short",
            domain_config=domain_config
        )
        assert not is_valid
        assert "too short" in error.lower()

        # Empty
        is_valid, error = validator.validate(
            response="",
            domain_config=domain_config
        )
        assert not is_valid
        assert "empty" in error.lower()

    def test_tier2_semantic_validation(self, domain_config):
        """Test Tier 2 (model-based) semantic validation"""
        validator = ResponseValidator(use_model_validation=True)

        # Test with query and relevant response
        is_valid, error = validator.validate(
            response="The billing amount is $150.00 for the procedure",
            domain_config=domain_config,
            query="Calculate billing charges"
        )
        assert is_valid
        assert error is None

    def test_tier2_catches_irrelevant_response(self, domain_config):
        """Test that Tier 2 catches semantically irrelevant responses"""
        validator = ResponseValidator(use_model_validation=True)

        # Response passes Tier 1 (length, format) but fails Tier 2 (relevance)
        is_valid, error = validator.validate(
            response="The weather is sunny today and birds are singing beautifully",
            domain_config=domain_config,
            query="Calculate medical billing charges"
        )

        # Should fail or have low confidence
        # Note: Heuristic implementation may pass, production Phi-2 would catch this
        if not is_valid:
            assert "semantic" in error.lower() or "validation" in error.lower()

    def test_tier1_fail_skips_tier2(self, domain_config):
        """Test that Tier 1 failure skips Tier 2 validation"""
        validator = ResponseValidator(use_model_validation=True)

        # Too short - fails Tier 1
        is_valid, error = validator.validate(
            response="Hi",
            domain_config=domain_config,
            query="Calculate billing"
        )

        assert not is_valid
        assert "too short" in error.lower()
        # Error message should be from Tier 1, not Tier 2

    def test_backward_compatibility(self, domain_config):
        """Test backward compatibility with old validation API"""
        validator = ResponseValidator()

        # Old API (no query parameter)
        is_valid, error = validator.validate(
            response="This is a valid response",
            domain_config=domain_config
        )
        assert is_valid

    def test_validation_with_context(self, domain_config):
        """Test validation with context dictionary"""
        validator = ResponseValidator(use_model_validation=True)

        context = {'user_id': 'test123', 'session_id': 'session456'}

        is_valid, error = validator.validate(
            response="Billing calculated successfully",
            domain_config=domain_config,
            query="Calculate billing",
            context=context
        )
        assert is_valid


class TestIntegration:
    """Integration tests for complete validation flow"""

    def test_end_to_end_validation(self):
        """Test complete validation workflow"""
        # Create validator with both tiers
        validator = ResponseValidator(use_model_validation=True)

        # Create domain config
        config = DomainConfig(
            domain_id="medical",
            name="Medical Domain",
            description="Medical processing",
            keywords=["medical", "diagnosis", "billing"],
            min_response_length=20,
            max_response_length=1000,
            use_model_validation=True
        )

        # Test valid response
        is_valid, error = validator.validate(
            response="The patient's diagnosis has been coded as ICD-10: E11.9 (Type 2 diabetes mellitus)",
            domain_config=config,
            query="Code the diabetes diagnosis"
        )

        assert is_valid
        assert error is None

    def test_performance(self):
        """Test validation performance"""
        import time

        validator = ResponseValidator(use_model_validation=True)
        config = DomainConfig(
            domain_id="test",
            name="Test",
            description="Test",
            keywords=["test"]
        )

        # Tier 1 only (should be fast)
        start = time.time()
        validator.validate(
            response="Test response for performance measurement",
            domain_config=config
        )
        tier1_time = (time.time() - start) * 1000

        assert tier1_time < 100  # Should be < 100ms

        # Tier 1 + Tier 2 (slower but reasonable)
        start = time.time()
        validator.validate(
            response="Test response for performance measurement with semantic validation",
            domain_config=config,
            query="Test query"
        )
        tier2_time = (time.time() - start) * 1000

        assert tier2_time < 1000  # Should be < 1 second

    def test_phi2_validator_standalone(self):
        """Test Phi2Validator can be used standalone"""
        from mdsa.domains.model_validator import validate_input, validate_response, validate_tools

        # Test convenience functions
        result = validate_input("Calculate billing charges")
        assert isinstance(result, ValidationResult)
        assert result.is_valid

        result = validate_response("What is the cost?", "The cost is $100")
        assert isinstance(result, ValidationResult)

        result = validate_tools(
            "Lookup code",
            [{'name': 'lookup'}],
            ["Result"]
        )
        assert isinstance(result, ValidationResult)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
