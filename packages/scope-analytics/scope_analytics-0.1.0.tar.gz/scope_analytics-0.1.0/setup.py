"""
Scope Analytics Backend SDK
AI-powered analytics for backend applications with automatic LLM conversation tracking
"""

from setuptools import setup, find_packages

# Read long description from README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="scope-analytics",
    version="0.1.0",
    author="Scope AI",
    author_email="support@scopeai.dev",
    description="AI-powered analytics SDK for backend applications with automatic LLM tracking",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/scopeai/scope-analytics-python",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "httpx>=0.24.0",  # Async HTTP client
        "python-dotenv>=1.0.0",  # Environment variable loading
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-mock>=3.10.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
        "openai": ["openai>=1.0.0"],
        "anthropic": ["anthropic>=0.18.0"],
        "langchain": ["langchain>=0.1.0"],
    },
    entry_points={
        "console_scripts": [
            "scope-run=scope_analytics.cli:main",
        ],
    },
)
