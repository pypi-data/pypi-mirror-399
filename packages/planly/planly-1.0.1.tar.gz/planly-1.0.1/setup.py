from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="planly",
    version="1.0.1",
    author="Planly.dev",
    description="Official Python SDK for Planly subscription validation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/planly-dev/planly-python",
    project_urls={
        "Bug Tracker": "https://github.com/planly-dev/planly-python/issues",
        "Documentation": "https://docs.planly.dev",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    py_modules=["planly"],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
)