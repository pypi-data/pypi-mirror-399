"""
AINative Python SDK Setup Configuration
Phase 1.3: Python SDK Core Structure
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "AINative Python SDK for unified database and AI operations"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]
    return [
        'requests>=2.25.0',
        'python-dateutil>=2.8.0',
        'typing-extensions>=4.0.0',
        'pydantic>=2.0.0',
        'httpx>=0.24.0',
        'aiohttp>=3.8.0',
        'numpy>=1.24.0',
        'PyYAML>=6.0.0',
        'python-dotenv>=1.0.0',
        'click>=8.1.0',
        'rich>=13.0.0',
        'tenacity>=8.2.0',
        'backoff>=2.2.0',
    ]

setup(
    name="ainative-python",
    version="2.0.0",
    author="AINative Team",
    author_email="support@ainative.studio",
    description="Official Python SDK for AINative Studio APIs with ZeroDB Local support",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/ainative/ainative-python",
    project_urls={
        "Documentation": "https://docs.ainative.studio/sdk/python",
        "API Reference": "https://api.ainative.studio/docs-enhanced",
        "Bug Reports": "https://github.com/ainative/studio/issues",
        "Source": "https://github.com/ainative/ainative-python",
    },
    packages=find_packages(exclude=['tests', 'tests.*', 'examples', 'examples.*']),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Database",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "isort>=5.10.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.2.0",
            "sphinx-autodoc-typehints>=1.19.0",
        ],
        "async": [
            "aiohttp>=3.8.0",
            "asyncio>=3.4.3",
        ],
    },
    entry_points={
        "console_scripts": [
            "ainative=ainative.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "ainative": ["py.typed"],
    },
    keywords=[
        "ainative", "database", "vector", "embedding", "ai", "ml",
        "machine learning", "artificial intelligence", "api", "sdk",
        "zerodb", "agent swarm", "postgresql", "vector search", "nosql",
        "table operations", "mongodb-style", "crud"
    ],
    zip_safe=False,
)