"""
Setup configuration for Django Context Memory
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

setup(
    name="django-context-memory",
    version="1.0.4",
    author="Gavin Holder",
    author_email="mangleholder@gmail.com",
    description="Deep code intelligence for AI assistants working with Django projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GavinHolder/django-context-memory",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Code Generators",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.0",
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
        # Core functionality has no dependencies
        # Django is optional - only needed if using Django management commands
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "flake8>=6.0",
            "mypy>=1.0",
        ],
        "django": [
            "Django>=3.2",
        ],
    },
    entry_points={
        "console_scripts": [
            "django-context=django_context_memory.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "django_context_memory": [
            "templates/*.md",
            "templates/*.txt",
            "templates/django_context_memory/*.html",
        ],
    },
    keywords="django ai claude code-intelligence context ast analysis",
    project_urls={
        "Bug Reports": "https://github.com/GavinHolder/django-context-memory/issues",
        "Source": "https://github.com/GavinHolder/django-context-memory",
        "Documentation": "https://github.com/GavinHolder/django-context-memory#readme",
    },
)
