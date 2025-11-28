"""
Ragamuffin Python SDK

Official Python client library for the Ragamuffin AI platform.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="ragamuffin-sdk",
    version="1.0.0",
    author="Ragamuffin Team",
    author_email="sdk@ragamuffin.ai",
    description="Official Python SDK for the Ragamuffin AI platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Stacey77/rag7",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "httpx>=0.24.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "respx>=0.20.0",
        ],
    },
    keywords=[
        "ragamuffin",
        "ai",
        "rag",
        "langflow",
        "vector-search",
        "embeddings",
        "llm",
        "sdk",
    ],
)
