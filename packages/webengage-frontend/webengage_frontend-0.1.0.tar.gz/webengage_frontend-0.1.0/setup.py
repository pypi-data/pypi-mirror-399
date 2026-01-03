"""
Setup script for webengage-frontend package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="webengage-frontend",
    version="0.1.0",
    author="WebEngage",
    author_email="support@webengage.com",
    description="A Python package for frontend-related functionality with chart visualization tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://repo.webengage.com/data-consultancy/data-science-consulting-master-repo",
    project_urls={
        "Homepage": "https://repo.webengage.com/data-consultancy/data-science-consulting-master-repo",
        "Documentation": "https://repo.webengage.com/data-consultancy/data-science-consulting-master-repo/-/blob/master/webengage-fe/README.md",
        "Repository": "https://repo.webengage.com/data-consultancy/data-science-consulting-master-repo",
        "Issues": "https://repo.webengage.com/data-consultancy/data-science-consulting-master-repo/-/issues",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.5.0",
        "matplotlib>=3.5.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
)

