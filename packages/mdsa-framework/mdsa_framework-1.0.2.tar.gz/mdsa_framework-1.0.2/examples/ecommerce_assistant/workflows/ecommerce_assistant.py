"""
E-commerce Assistant - Interactive Chatbot

Demonstrates MDSA framework for e-commerce customer service.
Routes queries to specialized domains: product_catalog, shopping_cart,
order_management, customer_service.
"""

import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from mdsa import MDSA
from domains.ecommerce_domains import register_domains


def main():
    print("\n" + "=" * 70)
    print(" E-COMMERCE ASSISTANT (Powered by MDSA)")
    print("=" * 70)
    print("\nDemonstrating domain-agnostic AI orchestration for e-commerce")
    print("\nAvailable domains:")
    print("  • Product Catalog  - Search, recommendations, specs")
    print("  • Shopping Cart    - Checkout, pricing, discounts")
    print("  • Order Management - Tracking, returns, shipping")
    print("  • Customer Service - Account, policies, support")
    print("\n" + "-" * 70)

    # Initialize MDSA
    print("\n[Initializing MDSA Framework...]")
    mdsa = MDSA(
        log_level="WARNING",
        enable_reasoning=True,
        enable_rag=False  # Set to True if you've initialized knowledge base
    )

    # Register e-commerce domains
    print("\n[Registering E-commerce Domains...]")
    register_domains(mdsa)

    print("\n" + "=" * 70)
    print("Ready! Type your query or 'quit' to exit")
    print("=" * 70)

    # Interactive loop
    while True:
        try:
            user_input = input("\nYou: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["quit", "exit", "q"]:
                print("\nThank you for using E-commerce Assistant!")
                break

            # Process request
            result = mdsa.process_request(user_input)

            # Display results
            print(f"\n[Routing Info]")
            print(f"  Domain: {result['metadata']['domain']}")
            print(f"  Confidence: {result['metadata']['confidence']:.1%}")
            print(f"  Latency: {result['metadata'].get('latency_ms', 0):.1f}ms")

            if result.get("response"):
                print(f"\nAssistant: {result['response']}")
            else:
                print(f"\nAssistant: Query routed to {result['metadata']['domain']} domain.")
                print(f"(Enable RAG for full responses)")

        except KeyboardInterrupt:
            print("\n\nInterrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            continue


if __name__ == "__main__":
    main()
