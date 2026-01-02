from setuptools import setup, find_packages

setup(
    name="utils",
    version="0.1.0",
    description="Common utility functions",
    author="Santhanalakshmi R",
    python_requires=">=3.9",
    packages=find_packages(),
    install_requires=[
        "pytest",
        "pytest-playwright",
        "pytest-html",
        "pytest-json-report",
        "playwright",
        "pytest-ordering"
    ],
    include_package_data=True,
)
