from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="sinkit",
    version="1.2.0",
    author="gosdrkht",
    description="Zero-dependency Sinhala NLP toolkit for Python — text cleaner, tokenizer, stopwords, sentiment analysis, profanity filter, transliterator, stemmer, keywords & RAG chunker",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gosdrkht/sinhala-toolkit",
    project_urls={
        "Homepage":    "https://www.sinhalatoolkit.leadingedgesolutions.lk",
        "Bug Reports": "https://github.com/gosdrkht/sinhala-toolkit/issues",
        "Source":      "https://github.com/gosdrkht/sinhala-toolkit",
    },
    packages=find_packages(where="python"),
    package_dir={"": "python"},
    entry_points={
        "console_scripts": [
            "sinkit=sinkit.cli:main",
        ],
    },
    data_files=[
        (
            "share/sinkit/data",
            [
                "data/stopwords.json",
                "data/common_words.json",
                "data/profanity.json",
            ],
        ),
    ],
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
    ],
    keywords="sinhala sinhala-nlp sinhalese singlish transliterator slugify stemmer nlp tokenizer text-processing text-cleaner stopwords sentiment-analysis profanity-filter rag llm unicode tamil sri-lanka natural-language-processing sinkit",
)
