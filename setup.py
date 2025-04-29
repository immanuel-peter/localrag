from setuptools import setup

setup(
    name="localrag",
    version="0.1.0",
    packages=["localrag"],
    install_requires=[
        "click>=8.0.0",
        "openai>=1.0.0",
        "anthropic>=0.5.0",
        "faiss-cpu>=1.7.0",
        "sentence-transformers>=2.2.0",
        "rich>=12.0.0",
        "requests>=2.28.0",
        "numpy>=1.20.0"
    ],
    entry_points={
        "console_scripts": [
            "localrag=localrag.cli:cli",
        ],
    },
)