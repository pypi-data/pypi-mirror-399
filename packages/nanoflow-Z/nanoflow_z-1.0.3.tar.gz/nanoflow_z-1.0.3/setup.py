
from setuptools import setup, find_packages

setup(
    name="nanoflow-Z",
    version="1.0.3",
    description="Run Giant LLMs on Low-End Hardware. Democratizing AI.",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Zousko",
    url="https://github.com/Zousko/nanoflow",
    packages=find_packages(),
    install_requires=[
        "torch>=2.0.0",
        "transformers>=4.30.0",
        "safetensors>=0.4.0",
        "huggingface_hub>=0.16.0",
        "psutil"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
)
