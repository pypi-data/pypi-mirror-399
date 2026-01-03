"""
Unit tests for Intent Router module.

Tests intent classification, domain registration, and routing logic.
"""

import unittest
from unittest.mock import patch, MagicMock
from mdsa.core.router import IntentRouter


class TestIntentRouter(unittest.TestCase):
    """Test suite for IntentRouter class."""

    def setUp(self):
        """Set up test fixtures."""
        # Initialize without loading actual model
        self.router = IntentRouter(device="cpu")

    def test_initialization(self):
        """Test IntentRouter initialization."""
        self.assertIsNotNone(self.router)
        self.assertEqual(self.router.device, "cpu")
        self.assertEqual(self.router.confidence_threshold, 0.85)
        self.assertEqual(len(self.router.domains), 0)

    def test_register_domain(self):
        """Test domain registration."""
        self.router.register_domain(
            "finance",
            "Financial transactions and banking",
            ["money", "transfer", "payment"]
        )

        self.assertIn("finance", self.router.domains)
        self.assertEqual(
            self.router.domains["finance"]["description"],
            "Financial transactions and banking"
        )
        self.assertEqual(
            self.router.domains["finance"]["keywords"],
            ["money", "transfer", "payment"]
        )

    def test_register_multiple_domains(self):
        """Test registering multiple domains."""
        self.router.register_domain("finance", "Financial operations", ["money"])
        self.router.register_domain("support", "Customer support", ["help"])
        self.router.register_domain("dev", "Development", ["code"])

        self.assertEqual(len(self.router.domains), 3)

    def test_classify_without_domains_raises_error(self):
        """Test classifying without registered domains raises error."""
        with self.assertRaises(ValueError):
            self.router.classify("Test query")

    def test_keyword_classification_single_match(self):
        """Test keyword-based classification with single match."""
        self.router.register_domain(
            "finance",
            "Financial operations",
            ["money", "transfer", "payment"]
        )
        self.router.register_domain(
            "support",
            "Customer support",
            ["help", "issue", "problem"]
        )

        domain, confidence = self.router.classify("I need help with my account")

        self.assertEqual(domain, "support")
        self.assertGreater(confidence, 0)

    def test_keyword_classification_multiple_matches(self):
        """Test keyword classification with multiple keyword matches."""
        self.router.register_domain(
            "finance",
            "Financial operations",
            ["money", "transfer", "payment", "balance"]
        )

        domain, confidence = self.router.classify(
            "Transfer money to check my balance"
        )

        self.assertEqual(domain, "finance")
        # Should have higher confidence due to multiple keyword matches
        self.assertGreater(confidence, 0)

    def test_keyword_classification_no_match(self):
        """Test keyword classification with no matches."""
        self.router.register_domain("finance", "Finance", ["money"])
        self.router.register_domain("support", "Support", ["help"])

        domain, confidence = self.router.classify("Random unrelated query")

        # Should return first domain with low confidence
        self.assertIn(domain, ["finance", "support"])
        self.assertEqual(confidence, 0.5)

    def test_keyword_classification_case_insensitive(self):
        """Test keyword classification is case-insensitive."""
        self.router.register_domain(
            "finance",
            "Finance",
            ["MONEY", "Transfer"]
        )

        domain, confidence = self.router.classify("transfer money")

        self.assertEqual(domain, "finance")
        self.assertGreater(confidence, 0)

    @patch('mdsa.core.router.TORCH_AVAILABLE', True)
    @patch('mdsa.core.router.AutoTokenizer')
    @patch('mdsa.core.router.AutoModel')
    @patch('mdsa.core.router.torch')
    def test_ml_classification_with_model(self, mock_torch, mock_model_class, mock_tokenizer_class):
        """Test ML-based classification when model is available."""
        # Setup mocks
        mock_tokenizer = MagicMock()
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

        mock_model = MagicMock()
        mock_model_class.from_pretrained.return_value = mock_model

        # Mock model output
        mock_output = MagicMock()
        mock_output.last_hidden_state = mock_torch.randn(1, 10, 768)
        mock_model.return_value = mock_output

        # Mock cosine similarity
        mock_torch.nn.functional.cosine_similarity.return_value = MagicMock(item=lambda: 0.92)

        router = IntentRouter()
        router.register_domain("finance", "Finance operations", ["money"])

        domain, confidence = router.classify("Transfer money")

        self.assertEqual(domain, "finance")
        # ML classification should work
        self.assertIsInstance(confidence, float)

    def test_get_domain_stats(self):
        """Test getting domain statistics."""
        self.router.register_domain("finance", "Finance", ["money"])
        self.router.register_domain("support", "Support", ["help"])

        # Classify some queries
        self.router.classify("transfer money")
        self.router.classify("transfer money")
        self.router.classify("need help")

        stats = self.router.get_domain_stats()

        self.assertEqual(stats["finance"]["query_count"], 2)
        self.assertEqual(stats["support"]["query_count"], 1)

    def test_reset_stats(self):
        """Test resetting domain statistics."""
        self.router.register_domain("finance", "Finance", ["money"])
        self.router.classify("transfer money")

        self.router.reset_stats()

        stats = self.router.get_domain_stats()
        self.assertEqual(stats["finance"]["query_count"], 0)

    def test_domain_query_count_increments(self):
        """Test query counts increment correctly."""
        self.router.register_domain("finance", "Finance", ["money"])

        initial_stats = self.router.get_domain_stats()
        self.assertEqual(initial_stats["finance"]["query_count"], 0)

        self.router.classify("transfer money")
        after_stats = self.router.get_domain_stats()
        self.assertEqual(after_stats["finance"]["query_count"], 1)

    def test_register_domain_without_keywords(self):
        """Test registering domain without keywords."""
        self.router.register_domain("finance", "Finance operations")

        self.assertIn("finance", self.router.domains)
        self.assertEqual(self.router.domains["finance"]["keywords"], [])

    def test_confidence_normalization(self):
        """Test confidence scores are normalized 0-1."""
        self.router.register_domain("finance", "Finance", ["money", "transfer"])

        domain, confidence = self.router.classify("transfer money")

        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)

    def test_repr(self):
        """Test string representation."""
        repr_str = repr(self.router)
        self.assertIn("IntentRouter", repr_str)
        self.assertIn("cpu", repr_str)


class TestIntentRouterEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""

    def test_empty_query(self):
        """Test classification with empty query."""
        router = IntentRouter()
        router.register_domain("finance", "Finance", ["money"])

        domain, confidence = router.classify("")

        self.assertEqual(domain, "finance")
        self.assertEqual(confidence, 0.5)  # No matches

    def test_very_long_query(self):
        """Test classification with very long query."""
        router = IntentRouter(max_length=128)
        router.register_domain("finance", "Finance", ["money"])

        long_query = "transfer money " * 100  # Very long
        domain, confidence = router.classify(long_query)

        self.assertEqual(domain, "finance")
        self.assertGreater(confidence, 0)

    def test_special_characters_in_query(self):
        """Test query with special characters."""
        router = IntentRouter()
        router.register_domain("finance", "Finance", ["money", "transfer"])

        domain, confidence = router.classify("Transfer $100 to @user!")

        self.assertEqual(domain, "finance")

    def test_register_same_domain_twice(self):
        """Test registering the same domain twice overwrites."""
        router = IntentRouter()
        router.register_domain("finance", "Description 1", ["keyword1"])
        router.register_domain("finance", "Description 2", ["keyword2"])

        self.assertEqual(
            router.domains["finance"]["description"],
            "Description 2"
        )

    def test_model_loading_failure_fallback(self):
        """Test fallback to keyword classification on model load failure."""
        with patch('mdsa.core.router.TORCH_AVAILABLE', False):
            router = IntentRouter()
            router.register_domain("finance", "Finance", ["money"])

            # Should use keyword fallback
            domain, confidence = router.classify("transfer money")

            self.assertEqual(domain, "finance")
            self.assertGreater(confidence, 0)

    def test_max_length_parameter(self):
        """Test max_length parameter is stored."""
        router = IntentRouter(max_length=64)
        self.assertEqual(router.max_length, 64)

    def test_confidence_threshold_parameter(self):
        """Test confidence_threshold parameter is stored."""
        router = IntentRouter(confidence_threshold=0.9)
        self.assertEqual(router.confidence_threshold, 0.9)

    def test_multiple_keywords_same_word(self):
        """Test multiple occurrences of same keyword."""
        router = IntentRouter()
        router.register_domain(
            "finance",
            "Finance",
            ["money"]
        )

        # Query has "money" multiple times
        domain, confidence = router.classify("money money money")

        self.assertEqual(domain, "finance")
        # Should only count once per keyword
        self.assertGreater(confidence, 0)


if __name__ == '__main__':
    unittest.main()
