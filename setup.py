from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="interview-toolkit",
    version="0.1.0",
    author="Nick G",
    author_email="nick@gm-sunshine.com",
    description="A comprehensive tool for generating and managing interview questions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GM-Sunshine/interview_toolkit",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "interview-toolkit=interview_toolkit:main",
        ],
    },
    include_package_data=True,
    package_data={
        "interview_toolkit": [
            "fonts/*",
            "logos/*",
        ],
    },
)
