# setup.py
from setuptools import setup

setup(
    name="tf-guard",
    version="1.0.2",
    py_modules=["main", "parser", "analyzer", "naming", "utils"],
    install_requires=["click", "openai", "rich", "python-dotenv"],
    entry_points={
        "console_scripts": [
            "ftltf=main:cli",
        ],
    },
)