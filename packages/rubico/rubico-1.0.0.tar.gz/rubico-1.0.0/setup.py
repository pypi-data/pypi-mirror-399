from setuptools import setup, find_packages

setup(
    name="rubico",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests"
    ],
    python_requires=">=3.8",
    description="Professional Rubika bot framework",
    author="TM",
    url="https://github.com/yourusername/rubico",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
