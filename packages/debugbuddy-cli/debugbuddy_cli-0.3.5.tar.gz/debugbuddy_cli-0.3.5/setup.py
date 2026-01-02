from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="debugbuddy-cli",
    version="0.3.5",
    license='MIT',
    author="DevArqf",
    author_email="devarqf@gmail.com",
    description="Your terminal's debugging companion - instant error explanations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DevArqf/DeBugBuddy",
    download_url="https://github.com/DevArqf/DeBugBuddy/archive/refs/tags/v0.3.5.tar.gz",
    keywords = ['python', 'debugging', 'cli'],
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Debuggers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "rich>=13.0.0",
    ],
    extras_require={
        "ai": [
            "openai>=2.8.1",
            "anthropic>=0.18.0",
        ],
        "github": [
            "PyGithub>=2.1.0",
        ],
        "watch": [
            "watchdog>=3.0.0",
        ],
        "full": [
            "openai>=2.8.1",
            "anthropic>=0.18.0",
            "PyGithub>=2.1.0",
            "watchdog>=3.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "dbug=debugbuddy.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "debugbuddy": ["patterns/*.json"],
    },
)