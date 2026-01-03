from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tft-report",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Automated TFT modeling with publication-ready report generation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sdkparkforbi/tft-report",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.9",
    install_requires=[
        "pandas>=1.5.0",
        "numpy>=1.21.0",
        "matplotlib>=3.5.0",
        "python-docx>=0.8.0",
        "openai>=1.0.0",
        "torch>=2.0.0",
        "pytorch-forecasting>=1.0.0",
        "lightning>=2.0.0",
    ],
)
