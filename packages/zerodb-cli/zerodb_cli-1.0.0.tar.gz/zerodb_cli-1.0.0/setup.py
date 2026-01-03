"""
Setup configuration for ZeroDB CLI
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="zerodb-cli",
    version="1.0.0",
    author="AINative Studio",
    author_email="hello@ainative.studio",
    description="ZeroDB Local CLI - Manage local ZeroDB environment and sync with cloud",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.ainative.studio",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Database",
        "Topic :: Database :: Database Engines/Servers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Environment :: Console",
        "Operating System :: OS Independent",
    ],
    keywords=[
        "zerodb",
        "database",
        "cli",
        "vector-database",
        "sync",
        "ainative",
        "AINative",
        "ai-database",
        "AI Database",
        "AINative Database",
        "vector-db",
        "embeddings",
        "semantic-search",
        "postgres",
        "postgresql",
        "docker",
        "docker-compose",
        "cloud-sync",
        "data-sync",
        "database-cli",
        "ai-native",
        "ai-tools",
        "machine-learning",
        "ml-database",
    ],
    project_urls={
        "Homepage": "https://www.ainative.studio",
        "Documentation": "https://docs.ainative.studio/zerodb-local",
    },
    python_requires=">=3.9",
    install_requires=[
        "typer>=0.9.0",
        "rich>=13.0.0",
        "requests>=2.31.0",
        "httpx>=0.24.0",
    ],
    py_modules=[
        "main",
        "config",
        "sync_planner",
        "sync_executor",
        "conflict_resolver",
    ],
    entry_points={
        "console_scripts": [
            "zerodb=main:app",
        ],
    },
)
