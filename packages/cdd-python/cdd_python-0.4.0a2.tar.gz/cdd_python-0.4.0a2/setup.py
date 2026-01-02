from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cdd-python",
    version="0.4.0a2",
    author="jemmyx",
    author_email="contact@cdd-framework.io",
    description="Python adapter for CDD (Cyberattack-Driven Development) framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cdd-framework/cdd-python",
    project_urls={
        "Bug Tracker": "https://github.com/cdd-framework/cdd-python/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Security",
    ],
    package_dir={"": "."},
    packages=find_packages(),
    package_data={
        "cdd_python": ["bin/cdd-core-*"],
    },
    python_requires=">=3.8",
)
