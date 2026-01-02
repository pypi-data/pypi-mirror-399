from setuptools import setup, find_packages

setup(
    name="ai-pose-generator-1",
    version="1766998.844.98",
    description="High-quality integration for https://supermaker.ai/image/ai-pose-generator/",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="SuperMaker",
    url="https://supermaker.ai/image/ai-pose-generator/",
    packages=find_packages(),
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
