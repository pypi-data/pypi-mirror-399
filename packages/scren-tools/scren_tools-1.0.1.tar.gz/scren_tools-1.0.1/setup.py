from setuptools import setup, find_packages

setup(
    name="scren_tools",
    version="1.0.1",
    packages=find_packages(),
    install_requires=[
        "requests",
        "pillow"
    ],
    python_requires='>=3.7',
    description="Ultimate full page screenshot library",
    author="Zeus",
    url="https://github.com/username/scrt",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
