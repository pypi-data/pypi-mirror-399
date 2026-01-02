from setuptools import setup, find_packages

setup(
    name="bananaproai-com",
    version="1767063.908.307",
    description="High-quality integration for https://bananaproai.com/",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="SuperMaker",
    url="https://bananaproai.com/",
    packages=find_packages(),
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
