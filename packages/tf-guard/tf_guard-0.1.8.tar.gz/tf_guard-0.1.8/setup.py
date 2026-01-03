# setup.py
from setuptools import setup

setup(
    name="tf-guard",
    version="0.1.8",
    py_modules=["main", "parser", "analyzer", "naming"],
    install_requires=["click", "openai", "rich", "python-dotenv"],
    entry_points={
        "console_scripts": [
            "ftltf=main:cli",
        ],
    },
)