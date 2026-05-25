from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="sinkit",
    version="1.0.0",
    author="gosdrkht",
    author_email="your@email.com",
    description="The missing developer toolkit for Sinhala language processing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gosdrkht/sinhala-toolkit",
    project_urls={
        "Bug Reports": "https://github.com/gosdrkht/sinhala-toolkit/issues",
        "Source":      "https://github.com/gosdrkht/sinhala-toolkit",
    },
    packages=find_packages(where="python"),
    package_dir={"": "python"},
    package_data={
        "sinkit": ["../../data/*.json"],
    },
    python_requires=">=3.8",
    install_requires=[],   # zero dependencies!
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Text Processing :: Linguistic",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Natural Language :: Sinhalese",
    ],
    keywords="sinhala nlp tokenizer text-processing sri-lanka sinhalese natural-language-processing",
)
