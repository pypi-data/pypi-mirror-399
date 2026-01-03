from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="astha-client",
    version="0.1.1",
    author="Ajay Yogal",
    author_email="ajay@astha.ai",
    description="Python SDK for Astha AI platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/asthaAi/astha-client-py",
    project_urls={
        "Bug Tracker": "https://github.com/asthaAi/astha-client-py/issues",
        "Documentation": "https://github.com/asthaAi/astha-client-py#readme",
        "Source": "https://github.com/asthaAi/astha-client-py",
    },
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=["mcp", "rbac", "oidc", "ai", "langchain", "agents", "astha", "sdk", "orchestration"],
    python_requires=">=3.11",
    install_requires=[
        "mcp-use>=1.5.1",
        "langchain-anthropic>=1.3.0",
        "httpx>=0.27.0",
        "mcp>=0.9.0",
        "python-dotenv>=1.2.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
            "mypy>=1.0.0",
        ],
        "jupyter": [
            "nest-asyncio>=1.5.0",
        ],
    },
)
