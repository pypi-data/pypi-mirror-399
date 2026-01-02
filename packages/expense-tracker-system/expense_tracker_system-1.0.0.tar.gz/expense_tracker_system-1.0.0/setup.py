from setuptools import setup, find_packages

setup(
    name="expense-tracker",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "sqlalchemy>=2.0.0",
        "pydantic>=2.0.0",
    ],
)