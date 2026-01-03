from setuptools import setup, find_packages

setup(
    name="rush-api",
    version="3.0.1",
    author="Rushabh Mavani",
    author_email="rushabhmavani01@gmail.com",
    description="The Universal API Framework. High-performance Custom JSON-over-TCP Protocol. Zero Dependencies.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[],  # Zero Dependencies
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="tcp api json protocol high-performance zero-dependency rush",
)
