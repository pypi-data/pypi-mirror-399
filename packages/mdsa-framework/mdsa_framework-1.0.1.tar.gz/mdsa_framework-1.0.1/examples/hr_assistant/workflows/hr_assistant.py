"""HR Assistant - Interactive Chatbot powered by MDSA"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from mdsa import MDSA
from domains.hr_domains import register_domains

def main():
    print("\n" + "=" * 70)
    print(" HR ASSISTANT (Powered by MDSA)")
    print("=" * 70)
    print("\nDomains: Recruitment | Onboarding | Benefits | Payroll")
    print("-" * 70)

    # Initialize
    print("\n[Initializing...]")
    mdsa = MDSA(log_level="WARNING", enable_reasoning=True, enable_rag=False)
    register_domains(mdsa)

    print("\n" + "=" * 70)
    print("Ready! Type your query or 'quit' to exit")
    print("=" * 70)

    # Interactive loop
    while True:
        try:
            user_input = input("\nYou: ").strip()
            if not user_input or user_input.lower() in ["quit", "exit", "q"]:
                print("\nGoodbye!")
                break

            result = mdsa.process_request(user_input)
            print(f"\n[{result['metadata']['domain']} - {result['metadata']['confidence']:.1%}]")
            if result.get("response"):
                print(f"Assistant: {result['response']}")
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")

if __name__ == "__main__":
    main()
