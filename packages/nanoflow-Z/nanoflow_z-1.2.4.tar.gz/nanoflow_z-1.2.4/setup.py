from setuptools import setup, find_packages
setup(
    name="nanoflow-Z",
    version="1.2.4",
    description="NanoFlow: Zero-RAM (Max 1.5GB) Engine",
    author="Zousko",
    url="https://github.com/Zousko/nanoflow",
    packages=find_packages(),
    install_requires=["torch", "transformers", "safetensors", "huggingface_hub", "psutil", "requests", "tqdm"],
)