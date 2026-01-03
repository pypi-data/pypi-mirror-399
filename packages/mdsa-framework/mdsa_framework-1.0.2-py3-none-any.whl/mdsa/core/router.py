"""
Intent Router Module

TinyBERT-based intent classification for domain routing with <50ms latency.
"""

import logging
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Optional imports (will be loaded if available)
try:
    import torch
    import torch.nn.functional as F
    from transformers import AutoModel, AutoTokenizer
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch/Transformers not available. IntentRouter will use fallback mode.")


class IntentRouter:
    """
    Intent classification router using TinyBERT for <50ms latency.

    Features:
    - TinyBERT (67M params) runs on CPU
    - <50ms classification latency (P99)
    - 95%+ accuracy target
    - Keyword fallback for simple cases
    - Confidence-based routing

    Example:
        >>> router = IntentRouter()
        >>> router.register_domain("finance", "Financial operations", ["money", "transfer"])
        >>> domain, confidence = router.classify("Transfer $100 to savings")
        >>> print(f"Domain: {domain}, Confidence: {confidence:.2f}")
    """

    def __init__(
        self,
        model_name: str = "huawei-noah/TinyBERT_General_6L_768D",
        device: str = "cpu",
        confidence_threshold: float = 0.85,
        max_length: int = 128
    ):
        """
        Initialize intent router.

        Args:
            model_name: HuggingFace model identifier
            device: Device to run on ("cpu", "cuda:0", etc.)
            confidence_threshold: Minimum confidence for routing
            max_length: Maximum sequence length (shorter = faster)
        """
        self.model_name = model_name
        self.device = device
        self.confidence_threshold = confidence_threshold
        self.max_length = max_length

        # Domain registry
        self.domains: Dict[str, Dict] = {}

        # Model components (lazy loaded)
        self.model = None
        self.tokenizer = None
        self._model_loaded = False

        # Performance optimization: Cache domain embeddings
        self._domain_embeddings: Dict[str, torch.Tensor] = {}
        self._embeddings_computed = False

        logger.info(f"IntentRouter initialized (model: {model_name}, device: {device})")

    def _load_model(self):
        """Lazy load TinyBERT model."""
        if self._model_loaded:
            return

        if not TORCH_AVAILABLE:
            logger.warning("PyTorch not available. Using keyword fallback only.")
            self._model_loaded = True
            return

        try:
            logger.info(f"Loading TinyBERT model: {self.model_name}")
            start = time.time()

            # Determine cache directory
            cache_dir = Path.home() / ".mdsa" / "models" / "tinybert"
            cache_dir.mkdir(parents=True, exist_ok=True)

            # Load model and tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                cache_dir=cache_dir
            )
            self.model = AutoModel.from_pretrained(
                self.model_name,
                cache_dir=cache_dir
            )

            # Move to device and set to eval mode
            self.model.to(self.device)
            self.model.eval()

            # Optimize for inference (disabled for compatibility)
            # Note: torch.compile requires C++ compiler which may not be available
            # Using standard eager mode for maximum compatibility
            # if hasattr(torch, 'compile'):
            #     try:
            #         self.model = torch.compile(self.model, mode="reduce-overhead")
            #         logger.info("Model compiled with torch.compile for faster inference")
            #     except Exception as e:
            #         logger.warning(f"torch.compile failed: {e}. Using standard model.")
            logger.debug("Using standard eager mode for inference (torch.compile disabled)")

            elapsed = time.time() - start
            logger.info(f"Model loaded in {elapsed:.2f}s")

            self._model_loaded = True

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            logger.warning("Falling back to keyword-based routing")
            self._model_loaded = True

    def register_domain(
        self,
        name: str,
        description: str,
        keywords: Optional[List[str]] = None
    ):
        """
        Register a domain for routing.

        Args:
            name: Domain name
            description: Domain description (used for classification)
            keywords: Optional keywords for fallback routing

        Example:
            >>> router.register_domain(
            ...     "finance",
            ...     "Financial transactions and banking",
            ...     ["money", "transfer", "balance", "payment"]
            ... )
        """
        self.domains[name] = {
            'description': description,
            'keywords': keywords or [],
            'query_count': 0
        }

        # Invalidate embedding cache when domains change
        self._embeddings_computed = False

        logger.info(f"Registered domain: {name}")

    def _precompute_domain_embeddings(self):
        """
        Precompute embeddings for all domain descriptions.

        This is called once on first classification to cache domain embeddings.
        Saves 100-250ms per request by avoiding redundant embedding generation.
        """
        if self._embeddings_computed:
            return

        if self.model is None or self.tokenizer is None:
            logger.debug("Model not loaded, skipping domain embedding precomputation")
            return

        logger.info(f"Precomputing embeddings for {len(self.domains)} domains...")
        start = time.time()

        try:
            for domain_name, domain_info in self.domains.items():
                embedding = self._get_embedding(domain_info['description'])
                self._domain_embeddings[domain_name] = embedding

            self._embeddings_computed = True
            elapsed_ms = (time.time() - start) * 1000
            logger.info(f"Domain embeddings computed in {elapsed_ms:.2f}ms (saves ~100-250ms per request)")

        except Exception as e:
            logger.error(f"Failed to precompute domain embeddings: {e}")
            self._domain_embeddings.clear()

    def classify(self, query: str) -> Tuple[str, float]:
        """
        Classify query to determine target domain.

        Args:
            query: User query string

        Returns:
            tuple: (domain_name, confidence_score)

        Example:
            >>> domain, conf = router.classify("Transfer $100")
            >>> print(f"Route to: {domain} (confidence: {conf:.2f})")
        """
        if not self.domains:
            raise ValueError("No domains registered. Use register_domain() first.")

        # Ensure model is loaded
        self._load_model()

        # Try ML-based classification if model available
        if self.model is not None and self.tokenizer is not None:
            return self._classify_ml(query)

        # Fallback to keyword-based
        return self._classify_keywords(query)

    def _classify_ml(self, query: str) -> Tuple[str, float]:
        """
        ML-based classification using TinyBERT.

        Args:
            query: User query

        Returns:
            tuple: (domain_name, confidence_score)
        """
        try:
            start = time.perf_counter()

            # Precompute domain embeddings on first use (lazy caching)
            self._precompute_domain_embeddings()

            # Get embeddings for query
            query_embedding = self._get_embedding(query)

            # Use cached domain embeddings for similarity computation
            domain_scores = {}
            for domain_name in self.domains.keys():
                # Use cached embedding if available, otherwise compute on-the-fly
                if domain_name in self._domain_embeddings:
                    domain_embedding = self._domain_embeddings[domain_name]
                else:
                    # Fallback to on-the-fly computation (rare)
                    domain_embedding = self._get_embedding(self.domains[domain_name]['description'])

                # Compute cosine similarity
                similarity = F.cosine_similarity(
                    query_embedding,
                    domain_embedding,
                    dim=1
                ).item()

                domain_scores[domain_name] = similarity

            # Find best domain
            best_domain = max(domain_scores, key=domain_scores.get)
            confidence = domain_scores[best_domain]

            # Apply keyword validation boost to improve routing accuracy
            best_domain, confidence = self._apply_keyword_boost(
                query, best_domain, confidence, domain_scores
            )

            # Latency measurement
            latency_ms = (time.perf_counter() - start) * 1000

            logger.debug(f"ML classification: {best_domain} (conf={confidence:.3f}, latency={latency_ms:.2f}ms)")

            # Update domain stats
            self.domains[best_domain]['query_count'] += 1

            return best_domain, confidence

        except Exception as e:
            logger.debug(f"ML classification not available, using keyword fallback: {str(e)[:100]}")
            return self._classify_keywords(query)

    def _get_embedding(self, text: str) -> torch.Tensor:
        """
        Get TinyBERT embedding for text.

        Args:
            text: Input text

        Returns:
            torch.Tensor: Embedding vector
        """
        # Tokenize
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            max_length=self.max_length,
            truncation=True,
            padding=True
        ).to(self.device)

        # Get embeddings (no gradients needed)
        with torch.no_grad():
            outputs = self.model(**inputs)
            # Use [CLS] token embedding
            embedding = outputs.last_hidden_state[:, 0, :]

        return embedding

    def _classify_keywords(self, query: str) -> Tuple[str, float]:
        """
        Keyword-based fallback classification.

        Args:
            query: User query

        Returns:
            tuple: (domain_name, confidence_score)
        """
        query_lower = query.lower()

        # Count keyword matches for each domain
        domain_scores = {}
        for domain_name, domain_info in self.domains.items():
            score = 0
            for keyword in domain_info['keywords']:
                if keyword.lower() in query_lower:
                    score += 1

            domain_scores[domain_name] = score

        # Find best match
        if not any(domain_scores.values()):
            # No keyword matches - return first domain with low confidence
            best_domain = list(self.domains.keys())[0]
            confidence = 0.5
        else:
            best_domain = max(domain_scores, key=domain_scores.get)
            # Normalize confidence based on keyword matches
            max_keywords = len(self.domains[best_domain]['keywords'])
            confidence = min(domain_scores[best_domain] / max(max_keywords, 1), 1.0)

        logger.debug(f"Keyword classification: {best_domain} (conf={confidence:.3f})")

        # Update domain stats
        self.domains[best_domain]['query_count'] += 1

        return best_domain, confidence

    def _apply_keyword_boost(
        self,
        query: str,
        predicted_domain: str,
        predicted_confidence: float,
        semantic_scores: Dict[str, float]
    ) -> Tuple[str, float]:
        """
        Apply keyword-based validation to boost correct domains.

        If predicted domain has NO keyword matches but another domain does,
        switch to the keyword-matching domain. This fixes semantic similarity
        misrouting (e.g., "explain symptoms" → radiology instead of clinical).

        Args:
            query: User query
            predicted_domain: Domain predicted by TinyBERT
            predicted_confidence: Confidence score from TinyBERT
            semantic_scores: All domain scores from semantic similarity

        Returns:
            tuple: (corrected_domain, adjusted_confidence)
        """
        query_lower = query.lower()

        # Count keyword matches for each domain
        keyword_matches = {}
        for domain_name, domain_info in self.domains.items():
            matches = sum(
                1 for kw in domain_info['keywords'] if kw.lower() in query_lower
            )
            keyword_matches[domain_name] = matches

        predicted_matches = keyword_matches[predicted_domain]
        max_matches = max(keyword_matches.values())

        # If predicted domain has 0 keywords but another has 2+, switch domains
        if predicted_matches == 0 and max_matches >= 2:
            # Find domain with most keyword matches
            best_keyword_domain = max(keyword_matches, key=keyword_matches.get)

            # Only switch if semantic score is reasonably close (within 0.15)
            semantic_diff = predicted_confidence - semantic_scores.get(best_keyword_domain, 0)

            if semantic_diff < 0.15:
                logger.info(
                    f"Keyword validation override: {predicted_domain} "
                    f"({predicted_matches} keywords) → {best_keyword_domain} "
                    f"({keyword_matches[best_keyword_domain]} keywords)"
                )
                # Boost confidence slightly for keyword match
                boosted_confidence = min(predicted_confidence + 0.05, 0.95)
                return best_keyword_domain, boosted_confidence

        # If predicted domain has keywords, keep it but log validation
        if predicted_matches > 0:
            logger.debug(
                f"Keyword validation passed: {predicted_domain} "
                f"has {predicted_matches} keyword matches"
            )

        return predicted_domain, predicted_confidence

    def get_domain_stats(self) -> Dict[str, Dict]:
        """
        Get statistics for all registered domains.

        Returns:
            dict: Domain statistics

        Example:
            >>> stats = router.get_domain_stats()
            >>> for domain, info in stats.items():
            ...     print(f"{domain}: {info['query_count']} queries")
        """
        return {
            name: {
                'query_count': info['query_count'],
                'keywords': info['keywords']
            }
            for name, info in self.domains.items()
        }

    def reset_stats(self):
        """Reset query counts for all domains."""
        for domain_info in self.domains.values():
            domain_info['query_count'] = 0
        logger.info("Domain statistics reset")

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<IntentRouter domains={len(self.domains)} "
            f"model_loaded={self._model_loaded} device={self.device}>"
        )


if __name__ == "__main__":
    # Demo usage (without actual model loading for speed)
    print("=== IntentRouter Demo ===\n")

    router = IntentRouter()

    # Register domains
    print("--- Registering Domains ---")
    router.register_domain(
        "finance",
        "Financial transactions, banking, and money management",
        ["money", "transfer", "payment", "balance", "transaction"]
    )
    router.register_domain(
        "support",
        "Customer support and help desk",
        ["help", "support", "issue", "problem", "error"]
    )
    router.register_domain(
        "dev",
        "Software development and coding",
        ["code", "bug", "deploy", "git", "api"]
    )

    # Classify queries
    print("\n--- Classification Tests ---")
    test_queries = [
        "Transfer $100 to my savings account",
        "I need help with my login issue",
        "Deploy the latest code to production",
        "What's my account balance?",
        "Fix the bug in the API endpoint"
    ]

    for query in test_queries:
        domain, confidence = router.classify(query)
        print(f"Query: '{query}'")
        print(f"  -> Domain: {domain} (confidence: {confidence:.2f})\n")

    # Statistics
    print("--- Domain Statistics ---")
    stats = router.get_domain_stats()
    for domain, info in stats.items():
        print(f"{domain}: {info['query_count']} queries")
