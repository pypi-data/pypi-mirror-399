"""
Setup script for trufflehog-processor
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read version from __init__.py
version_file = Path(__file__).parent / "trufflehog_processor" / "__init__.py"
version = "1.0.0"
if version_file.exists():
    for line in version_file.read_text().split("\n"):
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"').strip("'")
            break

setup(
    name="trufflehog-processor",
    version=version,
    description="Process and deduplicate TruffleHog scan results - filter verified and custom detector findings",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Amit Parjapat",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/trufflehog-processor",
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    exclude_package_data={
        '': [
            'example*.py',
            'build_and_install.sh',
            'publish.sh',
            'PUBLISH.md',
            '__pycache__',
            '*.pyc',
            '*.pyo',
        ],
    },
    python_requires=">=3.7",
    install_requires=[
        # No external dependencies - uses only standard library
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="trufflehog security secrets scanning deduplication filtering",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/trufflehog-processor/issues",
        "Source": "https://github.com/yourusername/trufflehog-processor",
    },
)

