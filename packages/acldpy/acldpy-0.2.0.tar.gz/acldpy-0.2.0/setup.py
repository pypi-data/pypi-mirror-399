from setuptools import setup, find_packages

try:
    with open("README.md", "r", encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "Long description not available."


setup(
    name='acldpy',
    version='0.2.0',
    packages=find_packages(),
    install_requires=[
        'numpy>=1.13.1',
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
)
