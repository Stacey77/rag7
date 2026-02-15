from setuptools import setup, find_packages

setup(
    name="agentic-infrastructure-platform",
    version="0.1.0",
    description="Multi-Agent Agentic Infrastructure Control Platform",
    author="Stacey Williams",
    packages=find_packages(),
    install_requires=[
        line.strip()
        for line in open("requirements.txt")
        if line.strip() and not line.startswith("#")
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "agentic-platform=agents.api.main:main",
        ],
    },
)
