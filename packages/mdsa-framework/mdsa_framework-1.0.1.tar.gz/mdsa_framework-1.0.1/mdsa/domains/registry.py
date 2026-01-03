"""
Domain Registry Module

Manages registration and lookup of domain configurations.
"""

import logging
from threading import Lock
from typing import Dict, List, Optional, Any

from mdsa.domains.config import DomainConfig

logger = logging.getLogger(__name__)


class DomainRegistry:
    """
    Thread-safe registry for managing domain configurations.

    Tracks registered domains and provides lookup functionality.
    """

    def __init__(self):
        """Initialize domain registry."""
        self._domains: Dict[str, DomainConfig] = {}
        self._lock = Lock()
        logger.info("DomainRegistry initialized")

    def register(self, config: DomainConfig) -> None:
        """
        Register a domain configuration.

        Args:
            config: Domain configuration to register

        Raises:
            ValueError: If domain_id already registered
        """
        with self._lock:
            if config.domain_id in self._domains:
                raise ValueError(
                    f"Domain '{config.domain_id}' is already registered. "
                    f"Use update() to modify existing domains."
                )

            self._domains[config.domain_id] = config
            logger.info(
                f"Domain '{config.domain_id}' registered "
                f"({config.name}, {len(config.keywords)} keywords)"
            )

    def update(self, config: DomainConfig) -> None:
        """
        Update an existing domain configuration.

        Args:
            config: Updated domain configuration

        Raises:
            ValueError: If domain_id not found
        """
        with self._lock:
            if config.domain_id not in self._domains:
                raise ValueError(
                    f"Domain '{config.domain_id}' not found. "
                    f"Use register() to add new domains."
                )

            self._domains[config.domain_id] = config
            logger.info(f"Domain '{config.domain_id}' updated")

    def get(self, domain_id: str) -> Optional[DomainConfig]:
        """
        Get domain configuration by ID.

        Args:
            domain_id: Domain identifier

        Returns:
            DomainConfig if found, None otherwise
        """
        with self._lock:
            return self._domains.get(domain_id)

    def unregister(self, domain_id: str) -> bool:
        """
        Unregister a domain.

        Args:
            domain_id: Domain identifier

        Returns:
            bool: True if domain was removed, False if not found
        """
        with self._lock:
            if domain_id in self._domains:
                del self._domains[domain_id]
                logger.info(f"Domain '{domain_id}' unregistered")
                return True
            return False

    def is_registered(self, domain_id: str) -> bool:
        """
        Check if a domain is registered.

        Args:
            domain_id: Domain identifier

        Returns:
            bool: True if domain is registered
        """
        with self._lock:
            return domain_id in self._domains

    def list_domains(self) -> List[str]:
        """
        Get list of all registered domain IDs.

        Returns:
            List of domain IDs
        """
        with self._lock:
            return list(self._domains.keys())

    def get_all(self) -> Dict[str, DomainConfig]:
        """
        Get all registered domains.

        Returns:
            Dictionary mapping domain IDs to configurations
        """
        with self._lock:
            return dict(self._domains)

    def find_by_keyword(self, keyword: str) -> List[DomainConfig]:
        """
        Find domains that match a keyword.

        Args:
            keyword: Keyword to search for (case-insensitive)

        Returns:
            List of matching domain configurations
        """
        keyword_lower = keyword.lower()
        with self._lock:
            matches = []
            for config in self._domains.values():
                if any(kw.lower() == keyword_lower for kw in config.keywords):
                    matches.append(config)
            return matches

    def get_stats(self) -> Dict[str, Any]:
        """
        Get registry statistics.

        Returns:
            Dictionary with statistics:
            - domains_registered: Number of domains
            - total_keywords: Total keywords across all domains
            - domains: Dict of domain ID to basic info
        """
        with self._lock:
            total_keywords = sum(
                len(config.keywords) for config in self._domains.values()
            )

            domains_info = {}
            for domain_id, config in self._domains.items():
                domains_info[domain_id] = {
                    "name": config.name,
                    "keywords_count": len(config.keywords),
                    "model": config.model_name,
                    "tier": config.model_tier.value,
                }

            return {
                "domains_registered": len(self._domains),
                "total_keywords": total_keywords,
                "domains": domains_info,
            }

    def clear(self) -> None:
        """Clear all registered domains."""
        with self._lock:
            count = len(self._domains)
            self._domains.clear()
            logger.info(f"DomainRegistry cleared ({count} domains removed)")

    def __len__(self) -> int:
        """Get number of registered domains."""
        with self._lock:
            return len(self._domains)

    def __repr__(self) -> str:
        with self._lock:
            return f"<DomainRegistry registered={len(self._domains)}>"

    def __contains__(self, domain_id: str) -> bool:
        """Check if domain is registered using 'in' operator."""
        return self.is_registered(domain_id)
