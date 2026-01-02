"""
Setup script for medimagecleaner package
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="medimagecleaner",
    version="0.2.0",
    author="Akinboye Yusuff",
    author_email="mailakinboye@gmail.com",
    description="Comprehensive package for removing PHI from medical images with face detection, risk assessment, and progress tracking",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/akinboye/medimagecleaner",
    project_urls={
        "Bug Tracker": "https://github.com/akinboye/medimagecleaner/issues",
        "Documentation": "https://github.com/akinboye/medimagecleaner#readme",
        "Source Code": "https://github.com/akinboye/medimagecleaner",
        "Author Website": "https://akinboye.dev/",
    },
    packages=find_packages(exclude=["tests", "tests.*", "examples"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    keywords=[
        "medical imaging",
        "dicom",
        "deidentification",
        "phi removal",
        "hipaa",
        "privacy",
        "face detection",
        "risk assessment",
        "healthcare",
        "anonymization",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pydicom>=2.3.0",
        "numpy>=1.20.0",
        "opencv-python>=4.5.0",
        "Pillow>=9.0.0",
    ],
    extras_require={
        "ocr": ["pytesseract>=0.3.9"],
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
            "twine>=4.0.0",
        ],
        "all": ["pytesseract>=0.3.9"],
    },
    entry_points={
        "console_scripts": [
            "medimagecleaner=medimagecleaner.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
