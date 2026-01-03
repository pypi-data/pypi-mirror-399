from setuptools import setup, find_packages

setup(
    name="nanoflow-Z",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'torch',
        'transformers',
        'safetensors',
        'huggingface_hub',
        'psutil'
    ],
)
