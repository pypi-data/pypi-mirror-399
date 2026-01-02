from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="guyteub",
    version="0.1.5",
    description="Outils pour afficher les stats GitHub dans un terminal",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Baptiste",
    author_email="",  # Ajoutez votre email si vous voulez
    url="https://github.com/votre-username/guyteub",  # Modifiez avec votre URL GitHub
    packages=find_packages(),
    install_requires=[
        "requests",
        "rich",
    ],
    entry_points={
        "console_scripts": [
            "guyteub=guyteub.app:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.6",
)
