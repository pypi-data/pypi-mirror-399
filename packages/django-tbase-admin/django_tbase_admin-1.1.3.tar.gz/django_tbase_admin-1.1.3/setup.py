#!/usr/bin/env python
"""
Django TBase Admin Setup Script
"""

from pathlib import Path
from setuptools import setup, find_packages

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="django-tbase-admin",
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    author="Terry Chan",
    author_email="terry@example.com",
    description="Django admin module for performance monitoring and database optimization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/terrychan/django-tbase-admin",
    packages=find_packages(where="src", exclude=["tests", "tests.*"]),
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Monitoring",
        "Topic :: Database",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Django>=3.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-django>=4.5",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.950",
        ],
        "docs": [
            "sphinx>=4.5",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    entry_points={
        "django.management.commands": [
            "tbase_clearsessions = tbase_admin.management.commands.clearsessions:Command",
            "tbase_clearhitcount = tbase_admin.management.commands.clearhitcount:Command",
        ],
    },
    keywords="django admin performance monitoring database optimization",
    project_urls={
        "Documentation": "https://django-tbase-admin.readthedocs.io/",
        "Source": "https://github.com/terrychan/django-tbase-admin/",
        "Tracker": "https://github.com/terrychan/django-tbase-admin/issues",
    },
)