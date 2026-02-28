"""Setup script for the rag7_agi package."""

from setuptools import setup, find_packages

setup(
    name="rag7_agi",
    version="0.1.0",
    author="Stacey Williams",
    description="Agentic AGI Robotics Framework",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "torch>=2.0.0",
        "torchvision>=0.15.0",
        "numpy>=1.24.0",
        "scipy>=1.10.0",
        "opencv-python>=4.7.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "llm": [
            "langchain>=0.1.0",
            "langchain-openai>=0.0.5",
            "langchain-community>=0.0.20",
            "openai>=1.0.0",
            "transformers>=4.30.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
