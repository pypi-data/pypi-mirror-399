"""
Setup configuration for HistoPCA package
"""
from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
try:
    long_description = (this_directory / "README.md").read_text(encoding='utf-8')
except:
    long_description = "Principal Component Analysis on Histogram-Binned Distributional Data"

setup(
    name="histopca",
    version="0.1.2",
    author="Bibi Brahim and Sun Makosso Alix",
    author_email="brahim_b@foursight.ai",
    maintainer="Bibi Brahim",
    maintainer_email="brahim_b@foursight.ai",
    description="Histogram-based Principal Component Analysis for distributional data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/brahim7/foursight.ai_histopca",
    project_urls={
        "Bug Tracker": "https://github.com/brahim7/foursight.ai_histopca/issues",
        "Documentation": "https://github.com/brahim7/foursight.ai_histopca#readme",
        "Source Code": "https://github.com/brahim7/foursight.ai_histopca",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "scipy>=1.7.0",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
    ],
    keywords="pca histogram distributional-data statistics",
    license="AGPL-3.0-or-later",
)
