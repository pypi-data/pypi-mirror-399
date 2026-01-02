from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cinetext",
    version="0.3.0",
    author="Anay Rustogi",
    author_email="codemaster.ar@gmail.com",
    description="A Python library for cinematic text effects in command-line interfaces.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/username/cinetext", # Replace with your GitHub URL
    py_modules=["cinetext"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Terminals",
    ],
    python_requires='>=3.6',
    install_requires=[],
)
