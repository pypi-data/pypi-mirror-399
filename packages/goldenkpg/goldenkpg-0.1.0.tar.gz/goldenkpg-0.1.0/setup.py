from setuptools import setup, find_packages

setup(
    name="goldenkpg",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    entry_points={
        "console_scripts": [
            "goldenkpg=goldenkpg.main:run",
        ],
    },
    author="Code Architect",
    description="A CLI tool to generate Operating System algorithm templates.",
    long_description=open("README.md", encoding="utf-8").read() if "README.md" in open("README.md", "a+").name else "A CLI tool to generate Operating System algorithm templates.",
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
