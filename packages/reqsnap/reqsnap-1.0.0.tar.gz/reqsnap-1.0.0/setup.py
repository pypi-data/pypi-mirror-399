

import setuptools
from pathlib import Path

# Read README
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

__version__ = "1.0.0"

REPO_NAME = "PyPI-Package---Requirements-snapshot-"
AUTHOR_USER_NAME = "Ahmed2797"
AUTHOR_EMAIL = "tanvirahmed754575@gmail.com"

setuptools.setup(
    name="reqsnap",
    version=__version__,
    author=AUTHOR_USER_NAME,
    author_email=AUTHOR_EMAIL,
    description="Python Requirements Snapshot Tool - Lock exact versions of main libraries",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=f"https://github.com/{AUTHOR_USER_NAME}/{REPO_NAME}",
    project_urls={
        "Bug Tracker": f"https://github.com/{AUTHOR_USER_NAME}/{REPO_NAME}/issues",
        "Documentation": f"https://github.com/{AUTHOR_USER_NAME}/{REPO_NAME}#readme",
        "Source Code": f"https://github.com/{AUTHOR_USER_NAME}/{REPO_NAME}",
    },
    packages=setuptools.find_packages(),
    install_requires=[
        "importlib-metadata>=4.0.0",
        "pyyaml>=6.0",
        "toml>=0.10.0",
        "packaging>=21.0",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "reqsnap=reqsnap.cli:main",
        ],
    },
    include_package_data=True,
    keywords="requirements, lock, snapshot, dependency, package",
)
