from setuptools import setup, find_packages

# Read the contents of your README file
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="windgrib",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A Python package for working with GRIB weather data files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yorfy/windgrib",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "xarray>=0.20.0",
        "s3fs>=2021.11.0",
        "requests>=2.26.0",
        "tqdm>=4.62.0",
        "cfgrib>=0.9.10.0",
        "dask>=2021.11.0",
        "netCDF4>=1.6.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
        "Development Status :: 3 - Alpha",
        "Natural Language :: English",
    ],
    keywords=["grib", "weather", "meteorology", "data", "forecast", "weather-data", "gfs", "ecmwf"],
    python_requires=">=3.7",
    project_urls={
        "Homepage": "https://github.com/yorfy/windgrib",
        "Bug Tracker": "https://github.com/yorfy/windgrib/issues",
        "Documentation": "https://github.com/yorfy/windgrib/blob/main/README.md",
    },
)