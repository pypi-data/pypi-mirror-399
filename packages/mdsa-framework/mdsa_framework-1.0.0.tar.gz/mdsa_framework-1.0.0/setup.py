"""
MDSA Setup Configuration

Install with: pip install .
Or for development: pip install -e .
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="mdsa",
    version="1.0.0",
    author="MDSA Team",
    author_email="your-email@example.com",
    description="Multi-Domain Small Language Model Agentic Orchestration Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mdsa",
    packages=find_packages(exclude=["tests", "tests.*", "docs"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "torch>=2.0.0",
        "transformers>=4.30.0",
        "numpy>=1.20.0",
        "psutil>=5.8.0",
    ],
    extras_require={
        "quantization": [
            "bitsandbytes>=0.41.0",
        ],
        "web": [
            "streamlit>=1.28.0",
            "plotly>=5.17.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
        ],
        "all": [
            "bitsandbytes>=0.41.0",
            "streamlit>=1.28.0",
            "plotly>=5.17.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "mdsa=mdsa.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
