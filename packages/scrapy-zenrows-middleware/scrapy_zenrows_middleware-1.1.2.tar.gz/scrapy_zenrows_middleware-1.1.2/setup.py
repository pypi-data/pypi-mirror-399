import re
from pathlib import Path

from setuptools import find_packages, setup

# Read version without importing the module
version_file = Path(__file__).parent / "scrapy_zenrows" / "__version__.py"
version_match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', version_file.read_text())
__version__ = version_match.group(1) if version_match else "0.0.0"

# Read long description from README
readme_path = Path(__file__).parent / "scrapy_zenrows" / "README.md"
long_description = readme_path.read_text(encoding="utf-8")

setup(
    name="scrapy-zenrows-middleware",
    version=__version__,
    description="A Scrapy middleware for accessing ZenRows Scraper API with minimal setup.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Idowu Omisola and Yuvraj Chandra",
    author_email="support@zenrows.com",
    url="https://github.com/ZenRows/scrapy-zenrows-middleware",
    packages=find_packages(),
    install_requires=[
        "scrapy>=2.0",
    ],
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: Scrapy",
    ],
    python_requires=">=3.8",
)
