"""
Setup script for Ancient Science of Numbers library.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ancient-science-of-numbers",
    version="0.1.0",
    author="Mthabis W. Mkwananzi",
    author_email="",
    description="A Python library implementing the numerology system from 'The Ancient Science of Numbers' by Luo Clement (1908)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sigasaint/ancient-science-of-numbers",
    packages=find_packages(exclude=("tests", "examples")),
    include_package_data=True,
    license="MIT",
    license_files=("LICENSE",),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9,<4",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "wheel>=0.40.0",
            "build>=0.10.0",
        ],
    },
    project_urls={
        "Source": "https://github.com/sigasaint/ancient-science-of-numbers",
        "Bug Tracker": "https://github.com/sigasaint/ancient-science-of-numbers/issues",
        "Documentation": "https://github.com/sigasaint/ancient-science-of-numbers#readme",
    },
    keywords=["numerology", "numbers", "ancient science", " Luo Clement"],
    zip_safe=False,
)

