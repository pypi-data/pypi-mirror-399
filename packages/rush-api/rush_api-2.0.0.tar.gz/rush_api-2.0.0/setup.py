from setuptools import setup, find_packages

setup(
    name="rush-api",
    version="2.0.0",
    author="Rushabh Mavani",
    author_email="rushabhmavani01@gmail.com",
    description="Zero-Dependency AI-Native Protocol Framework. Replaces requests, FastAPI, and BeautifulSoup.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[],  # Zero Dependencies
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="http api rest ai agent protocol zero-dependency",
)
