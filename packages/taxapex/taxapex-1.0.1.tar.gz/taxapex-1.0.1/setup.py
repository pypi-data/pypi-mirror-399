"""
TaxApex Python SDK Setup
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="taxapex",
    version="1.0.1",
    author="Innorve",
    author_email="support@innorve.ai",
    description="Python SDK for the TaxApex Tax Notice Management API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/innorve/taxapex-python",
    project_urls={
        "Documentation": "https://docs.taxapex.com",
        "Bug Tracker": "https://github.com/innorve/taxapex-python/issues",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial :: Accounting",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "responses>=0.23.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
            "types-requests>=2.28.0",
        ],
    },
)
