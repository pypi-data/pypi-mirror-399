"""
Response Validator Module

Two-tier validation for responses from domain SLMs:
- Tier 1: Fast rule-based validation (length, toxicity, repetition)
- Tier 2: Model-based semantic validation using Phi-2 (optional)
"""

import logging
import re
from typing import Tuple, Optional, List, Dict, Any

from mdsa.domains.config import DomainConfig

logger = logging.getLogger(__name__)


class ResponseValidator:
    """
    Two-tier validator for domain SLM responses.

    Tier 1 (Fast): Rule-based checks (length, toxicity, repetition)
    Tier 2 (Semantic): Phi-2 model-based validation (optional)

    Checks response length, content quality, and domain relevance.
    """

    def __init__(self, use_model_validation: bool = False):
        """
        Initialize response validator.

        Args:
            use_model_validation: Enable Phi-2 model-based validation (Tier 2)
        """
        self.use_model_validation = use_model_validation
        self._model_validator = None

        # Lazy load model validator only if needed
        if use_model_validation:
            try:
                from mdsa.domains.model_validator import Phi2Validator
                self._model_validator = Phi2Validator()
                logger.info("Two-tier validation enabled (rule-based + Phi-2)")
            except ImportError:
                logger.warning("Phi2Validator not available, falling back to rule-based only")
                self.use_model_validation = False
        else:
            logger.debug("Rule-based validation only (Tier 1)")

        logger.debug("ResponseValidator initialized")

    def validate(
        self,
        response: str,
        domain_config: DomainConfig,
        query: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Two-tier validation of response.

        Tier 1: Fast rule-based checks (always run)
        Tier 2: Semantic model-based validation (if enabled)

        Args:
            response: Generated response
            domain_config: Domain configuration
            query: Optional user query (for semantic validation)
            context: Optional context dictionary

        Returns:
            Tuple of (is_valid, error_message)
            If valid, error_message is None
        """
        # === TIER 1: Fast Rule-Based Validation ===

        # Check if response is empty
        if not response or not response.strip():
            return False, "Response is empty"

        # Check minimum length
        if len(response) < domain_config.min_response_length:
            return False, (
                f"Response too short ({len(response)} chars, "
                f"min: {domain_config.min_response_length})"
            )

        # Check maximum length
        if len(response) > domain_config.max_response_length:
            return False, (
                f"Response too long ({len(response)} chars, "
                f"max: {domain_config.max_response_length})"
            )

        # Check for repetition (simple check)
        if self._has_excessive_repetition(response):
            return False, "Response contains excessive repetition"

        # Check for incomplete sentences (very basic check)
        if self._appears_incomplete(response):
            logger.warning("Response may be incomplete")
            # Don't fail, just warn

        # Check toxicity if enabled
        if domain_config.check_toxicity:
            is_safe, toxicity_msg = self.check_toxicity(response)
            if not is_safe:
                return False, toxicity_msg

        logger.debug(f"Tier 1 validation passed ({len(response)} chars)")

        # === TIER 2: Model-Based Semantic Validation ===

        if self.use_model_validation and self._model_validator and query:
            logger.debug("Running Tier 2 semantic validation...")

            # Validate response relevance to query
            validation_result = self._model_validator.validate_response(
                query=query,
                response=response,
                context=context
            )

            if not validation_result.is_valid:
                error_msg = f"Semantic validation failed: {', '.join(validation_result.issues)}"
                logger.warning(error_msg)
                return False, error_msg

            if validation_result.warnings:
                for warning in validation_result.warnings:
                    logger.warning(f"Semantic validation warning: {warning}")

            logger.debug(
                f"Tier 2 validation passed (confidence={validation_result.confidence:.2f})"
            )

        # All checks passed
        logger.debug(f"Response validation passed (two-tier)")
        return True, None

    def check_length(
        self,
        response: str,
        min_length: int,
        max_length: int
    ) -> bool:
        """
        Check if response is within length bounds.

        Args:
            response: Response text
            min_length: Minimum length in characters
            max_length: Maximum length in characters

        Returns:
            bool: True if within bounds
        """
        length = len(response)
        return min_length <= length <= max_length

    def check_toxicity(self, response: str) -> Tuple[bool, Optional[str]]:
        """
        Check for toxic content.

        Note: This is a placeholder implementation.
        In production, use a proper toxicity detection model.

        Args:
            response: Response text

        Returns:
            Tuple of (is_safe, error_message)
        """
        # Simple keyword-based check (not robust)
        # In production, use detoxify or similar libraries
        toxic_patterns = [
            r'\b(hate|kill|die|stupid|idiot)\b',  # Very basic check
        ]

        for pattern in toxic_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                logger.warning("Potential toxic content detected")
                return False, "Response contains potentially inappropriate content"

        return True, None

    def check_relevance(
        self,
        response: str,
        domain_config: DomainConfig,
        query: Optional[str] = None
    ) -> bool:
        """
        Check if response is relevant to the domain.

        Args:
            response: Response text
            domain_config: Domain configuration
            query: Optional user query for context

        Returns:
            bool: True if response appears relevant
        """
        # Simple relevance check based on domain keywords
        response_lower = response.lower()

        # Check if response contains any domain keywords
        matching_keywords = [
            kw for kw in domain_config.keywords
            if kw.lower() in response_lower
        ]

        if matching_keywords:
            logger.debug(
                f"Response contains {len(matching_keywords)} domain keywords"
            )
            return True

        # If query is provided, check if response relates to it
        if query:
            query_words = set(query.lower().split())
            response_words = set(response_lower.split())
            overlap = query_words & response_words

            if len(overlap) > 0:
                logger.debug(f"Response has {len(overlap)} words overlapping with query")
                return True

        # Couldn't determine relevance, assume it's okay
        logger.warning("Could not verify response relevance")
        return True

    def _has_excessive_repetition(self, text: str, threshold: int = 5) -> bool:
        """
        Check if text has excessive repetition.

        Args:
            text: Text to check
            threshold: Number of repetitions to consider excessive

        Returns:
            bool: True if excessive repetition found
        """
        # Split into words
        words = text.lower().split()

        if len(words) < threshold:
            return False

        # Check for repeated words
        for i in range(len(words) - threshold + 1):
            word = words[i]
            # Count consecutive occurrences
            count = 1
            for j in range(i + 1, len(words)):
                if words[j] == word:
                    count += 1
                else:
                    break

            if count >= threshold:
                logger.debug(f"Found {count} repetitions of '{word}'")
                return True

        # Check for repeated phrases
        for phrase_len in range(3, 6):  # Check phrases of 3-5 words
            for i in range(len(words) - phrase_len * 2):
                phrase = tuple(words[i:i + phrase_len])
                # Check if this exact phrase repeats immediately
                next_phrase = tuple(words[i + phrase_len:i + phrase_len * 2])
                if phrase == next_phrase:
                    logger.debug(f"Found repeated phrase: {' '.join(phrase)}")
                    return True

        return False

    def _appears_incomplete(self, text: str) -> bool:
        """
        Check if response appears incomplete.

        Args:
            text: Text to check

        Returns:
            bool: True if text appears incomplete
        """
        text = text.strip()

        # Check if ends with sentence terminator
        if text and text[-1] not in '.!?':
            # Might be incomplete
            return True

        # Check if last "sentence" is too short
        sentences = re.split(r'[.!?]', text)
        if sentences:
            last_sentence = sentences[-1].strip()
            if last_sentence and len(last_sentence) < 5:
                return True

        return False

    def sanitize_response(self, response: str) -> str:
        """
        Sanitize response by removing problematic content.

        Args:
            response: Raw response

        Returns:
            Sanitized response
        """
        # Remove excessive whitespace
        response = re.sub(r'\s+', ' ', response)

        # Remove leading/trailing whitespace
        response = response.strip()

        # Remove markdown artifacts if present
        response = response.replace('**', '')
        response = response.replace('##', '')

        # Remove potential prompt leakage
        # (if model outputs its own prompt)
        prompt_indicators = ['System:', 'User:', 'Assistant:', 'Query:']
        for indicator in prompt_indicators:
            if response.startswith(indicator):
                response = response.split(indicator, 1)[1].strip()

        return response

    def truncate_to_sentence(self, response: str, max_length: int) -> str:
        """
        Truncate response to last complete sentence within max_length.

        Args:
            response: Response to truncate
            max_length: Maximum length

        Returns:
            Truncated response
        """
        if len(response) <= max_length:
            return response

        # Truncate to max_length
        truncated = response[:max_length]

        # Find last sentence terminator
        last_period = max(
            truncated.rfind('.'),
            truncated.rfind('!'),
            truncated.rfind('?')
        )

        if last_period > 0:
            # Truncate to last complete sentence
            return truncated[:last_period + 1]
        else:
            # No sentence terminator found, return truncated + ellipsis
            return truncated + "..."

    def __repr__(self) -> str:
        return "<ResponseValidator>"
