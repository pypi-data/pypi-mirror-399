#!/usr/bin/env python3

from setuptools import setup, find_packages
import os

# Read README with proper encoding handling
def read_readme():
    readme_path = "README.md"
    if os.path.exists(readme_path):
        try:
            with open(readme_path, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            with open(readme_path, "r", encoding="latin-1") as f:
                return f.read()
    return "MLE Runtime - High-Performance Machine Learning Inference Engine"

setup(
    name="mle_runtime",
    version="2.0.4",
    description="MLE Runtime - High-Performance Machine Learning Inference Engine",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Vinay Kamble",
    author_email="vinaykamble289@gmail.com",
    url="https://github.com/vinaykamble289/mle-runtime",
    project_urls={
        "Bug Reports": "https://github.com/vinaykamble289/mle-runtime/issues",
        "Source": "https://github.com/vinaykamble289/mle-runtime",
        "Documentation": "https://github.com/vinaykamble289/mle-runtime#readme",
    },
    packages=find_packages(),
    package_data={
        'mle_runtime': ['*.pyd', '*.so', '*.dll'],
    },
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "scipy>=1.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-benchmark>=3.4.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: C++",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="machine learning, inference, runtime, optimization, performance, scikit-learn, pytorch, xgboost, lightgbm, catboost, neural networks, deep learning, model deployment, production, c++, cuda, gpu acceleration",
)