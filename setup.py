from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="gaitalytics",
    version="0.1.7beta",
    author="André Böni",
    author_email="andre.boeni@cereneo.foundation",
    url="https://github.com/cereneo-foundation/gaitalytics",
    description="Library to analyse gait data captured with a mocap system",
    long_description="file: README.md",
    long_description_content_type="text/markdown",
    keywords="gait, analysis, c3d, mocap",
    license="MIT",
    python_requires="==3.8.*",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages = find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pandas",
        "pyyaml",
        "matplotlib",
        "numpy",
        "scipy"]
)
