"""
MDSA CLI Commands

Run with: mdsa
Or: python -m mdsa
"""

import sys
from mdsa import __version__, HardwareDetector


def show_welcome():
    """Display welcome page."""
    print("""
========================================================================
                           
   M D S A   F R A M E W O R K
                           
   Multi-Domain Small Language Model Agentic Framework             
                                                                    
========================================================================

Installation Successful!

Version: {}
Python: {}.{}.{}

""".format(__version__, sys.version_info.major, sys.version_info.minor, sys.version_info.micro))

    # Detect hardware
    try:
        detector = HardwareDetector()
        hw = detector.get_summary()
        print(f"""Hardware Detected:
   CPU: {hw["cpu_cores"]} cores
   RAM: {hw["memory_gb"]:.1f} GB
   GPU: {"Available" if hw.get("has_cuda") or hw.get("has_mps") else "Not detected"}
""")
    except:
        print("Hardware: Detection skipped\n")

    print("""
Quick Start:

1. Basic Usage:
   >>> from mdsa import ModelManager, DomainExecutor, create_finance_domain
   >>> 
   >>> manager = ModelManager()
   >>> executor = DomainExecutor(manager)
   >>> finance = create_finance_domain()
   >>> 
   >>> result = executor.execute("What's my balance?", finance)
   >>> print(result['response'])

2. Use ANY HuggingFace Model:
   >>> from mdsa import DomainConfig
   >>> 
   >>> custom_domain = DomainConfig(
   ...     domain_id="custom",
   ...     name="My Domain",
   ...     description="Custom domain",
   ...     keywords=["keyword1", "keyword2"],
   ...     model_name="microsoft/phi-2",  # ANY model!
   ...     system_prompt="You are a helpful assistant"
   ... )

3. Monitor Performance:
   >>> from mdsa import RequestLogger, MetricsCollector
   >>> 
   >>> logger = RequestLogger()
   >>> metrics = MetricsCollector()
   >>> 
   >>> stats = logger.get_stats()
   >>> summary = metrics.get_summary()

Documentation: https://github.com/yourusername/mdsa
Examples: examples/
Help: mdsa --help

""")


def show_version():
    """Show version info."""
    print(f"MDSA version {__version__}")


def show_help():
    """Show help text."""
    print("""
MDSA - Multi-Domain SLM Agentic Framework

Usage:
  mdsa              Show welcome page
  mdsa --version    Show version
  mdsa --help       Show this help

For Python usage:
  python -m mdsa

Documentation: https://github.com/yourusername/mdsa
""")


def main():
    """Main CLI entry point."""
    args = sys.argv[1:]
    
    if not args:
        show_welcome()
    elif args[0] in ["--version", "-v"]:
        show_version()
    elif args[0] in ["--help", "-h"]:
        show_help()
    else:
        print(f"Unknown command: {args[0]}")
        print("Run 'mdsa --help' for usage information")
        sys.exit(1)


if __name__ == "__main__":
    main()
