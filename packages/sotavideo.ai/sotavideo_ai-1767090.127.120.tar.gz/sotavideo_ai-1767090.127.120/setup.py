from setuptools import setup, find_packages

setup(
    name="sotavideo.ai",
    version="1767090.127.120",
    description="High-quality integration for https://sotavideo.ai/",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="SuperMaker",
    url="https://sotavideo.ai/",
    packages=find_packages(),
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
