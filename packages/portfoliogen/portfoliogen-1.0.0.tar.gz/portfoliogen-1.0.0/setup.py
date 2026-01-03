"""
Setup script for PortfolioGen package.
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "A Python package for generating portfolio project folders."

setup(
    name="portfoliogen",
    version="1.0.0",
    author="Sameer Lamichhane",
    author_email="sameerlamichhane00@gmail.com",
    description="Automatic portfolio project generator",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/sameer-lamichhane/portfolio-gen",
    packages=find_packages(),
    package_data={
        'portfoliogen': [
            'templates/*/*.html',
            'templates/*/*.css', 
            'templates/*/*.js',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.7",
    install_requires=[
        'importlib-resources>=1.3.0; python_version<"3.9"',
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "portfoliogen=portfoliogen.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="portfolio generator html css javascript web development",
    project_urls={
        "Bug Reports": "https://github.com/sameer-lamichhane/portfolio-gen/issues",
        "Source": "https://github.com/sameer-lamichhane/portfolio-gen",
        "Documentation": "https://github.com/sameer-lamichhane/portfolio-gen#readme",
    },
)