from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="marketo-rest-api-wrapper",
    version="1.0.0",
    author="Talha",
    description="A comprehensive Python wrapper for the Marketo REST API with auth management, rate limiting, pagination, and bulk operations.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/talhathecoder/marketo-rest-api-wrapper",
    packages=find_packages(exclude=["tests*", "examples*", "docs*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "requests>=2.28.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "responses>=0.23",
            "black>=23.0",
            "ruff>=0.1.0",
            "mypy>=1.0",
        ]
    },
    keywords="marketo api adobe marketing-automation leads crm rest-api",
    project_urls={
        "Bug Tracker": "https://github.com/talhathecoder/marketo-rest-api-wrapper/issues",
        "Documentation": "https://github.com/talhathecoder/marketo-rest-api-wrapper/docs",
        "Source Code": "https://github.com/talhathecoder/marketo-rest-api-wrapper",
    },
)
