"""Setup configuration for the vision package."""

from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = [
        line.strip()
        for line in f
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="vision",
    version="1.0.0",
    description="Computer vision module for a robotics AGI system",
    packages=find_packages(exclude=["tests*"]),
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.0.0",
        ],
        "esrgan": [
            "realesrgan>=0.3.0",
            "basicsr>=1.4.2",
        ],
    },
    include_package_data=True,
    package_data={
        "vision": ["config/*.yaml"],
    },
    entry_points={
        "console_scripts": [],
    },
)
