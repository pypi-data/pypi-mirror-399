from setuptools import setup, find_packages
from setuptools.command.install import install
import sys

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# System dependencies note
SYSTEM_REQUIREMENTS = """
## System Requirements

This package requires the following system tools to be installed:

- **Git**: Version 2.0 or higher
  - Windows: https://git-scm.com/download/win
  - macOS: `brew install git`
  - Linux: `apt-get install git` or `yum install git`

- **GitHub CLI (gh)**: Version 2.0 or higher
  - Windows: `choco install gh` or download from https://cli.github.com
  - macOS: `brew install gh`
  - Linux: https://cli.github.com/manual/installation

After installation, authenticate with GitHub:
```bash
gh auth login
```
"""


class PostInstallCommand(install):
    """Custom install command to run post-install setup"""
    def run(self):
        install.run(self)
        # Run post-install script
        try:
            from errlog_smartgit.post_install import post_install
            post_install()
        except Exception as e:
            print(f"Warning: Post-install setup failed: {e}")


setup(
    name="pypi-errlog-smartgit",
    version="1.3.0",
    author="Abu Shariff",
    author_email="abu.shariffaiml@gmail.com",
    description="errlog-smartgit - SmartGit Error Handler with detailed feedback",
    long_description=long_description + "\n\n" + SYSTEM_REQUIREMENTS,
    long_description_content_type="text/markdown",
    url="https://github.com/abucodingai/errlog-smartgit-py",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control :: Git",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "smartgit-err=errlog_smartgit.cli:main",
        ],
    },
    install_requires=[
        "pypi-smartgit>=1.0.0",
        "colorama>=0.4.4",
    ],
    extras_require={
        "dev": ["pytest>=7.0", "black>=22.0", "flake8>=4.0"],
    },
    project_urls={
        "GitHub CLI": "https://cli.github.com",
        "Documentation": "https://github.com/abucodingai/errlog-smartgit-py",
    },
    cmdclass={
        'install': PostInstallCommand,
    },
)
