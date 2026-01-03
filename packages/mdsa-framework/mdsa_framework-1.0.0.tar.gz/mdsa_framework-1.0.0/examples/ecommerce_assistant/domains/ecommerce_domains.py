"""
E-commerce Domain Definitions

Defines the four specialized domains for e-commerce customer service.
"""

from typing import Dict, List


def get_ecommerce_domains() -> List[Dict[str, any]]:
    """
    Returns domain configurations for e-commerce assistant.

    Returns:
        List of domain dictionaries with name, description, and keywords
    """
    return [
        {
            "name": "product_catalog",
            "description": "Product search, recommendations, specifications, and inventory",
            "keywords": [
                "product", "search", "find", "show", "recommend", "best", "top",
                "specs", "specification", "stock", "available", "inventory", "item",
                "compare", "review", "rating", "model", "brand", "category"
            ]
        },
        {
            "name": "shopping_cart",
            "description": "Shopping cart management, checkout, pricing, discounts, and payment",
            "keywords": [
                "cart", "checkout", "price", "discount", "coupon", "payment", "pay",
                "total", "tax", "promo", "promotion", "add", "remove", "quantity",
                "subtotal", "credit", "debit", "PayPal", "ApplePay"
            ]
        },
        {
            "name": "order_management",
            "description": "Order tracking, returns, refunds, shipping, and order modifications",
            "keywords": [
                "order", "track", "return", "refund", "cancel", "delivery", "shipping",
                "package", "exchange", "modify", "status", "estimated", "arrived",
                "shipment", "carrier", "tracking number", "reroute"
            ]
        },
        {
            "name": "customer_service",
            "description": "Customer support, account management, policies, and general inquiries",
            "keywords": [
                "support", "help", "contact", "service", "policy", "account", "reset",
                "update", "complaint", "feedback", "question", "assistance", "issue",
                "problem", "password", "email", "profile", "notification", "privacy"
            ]
        }
    ]


def register_domains(mdsa):
    """
    Register all e-commerce domains with MDSA orchestrator.

    Args:
        mdsa: MDSA orchestrator instance
    """
    domains = get_ecommerce_domains()

    for domain in domains:
        mdsa.register_domain(
            name=domain["name"],
            description=domain["description"],
            keywords=domain["keywords"]
        )
        print(f"✓ Registered domain: {domain['name']}")

    print(f"\n{len(domains)} e-commerce domains registered successfully!")
    return domains
