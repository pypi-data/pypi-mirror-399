
from setuptools import setup, find_packages

setup(
    name="nanoflow-Z",
    version="1.0.6",
    description="Full NanoFlow Library Rebuilt",
    long_description="Complete rebuild to fix missing modules.",
    long_description_content_type="text/markdown",
    author="Zousko",
    url="https://github.com/Zousko/nanoflow",
    packages=find_packages(), # CA C'EST CRUCIAL
    install_requires=["torch", "transformers", "safetensors", "huggingface_hub", "psutil", "requests", "tqdm"],
)
