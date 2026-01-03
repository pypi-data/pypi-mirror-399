from setuptools import setup, find_packages
setup(
    name="nanoflow-Z",
    version="1.2.2",
    description="NanoFlow: Zero-RAM loading for Giant Models",
    author="Zousko",
    url="https://github.com/Zousko/nanoflow",
    packages=find_packages(),
    install_requires=["torch", "transformers", "safetensors", "huggingface_hub", "psutil", "requests", "tqdm"],
)