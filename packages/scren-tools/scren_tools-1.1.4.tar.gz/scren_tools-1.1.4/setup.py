from setuptools import setup, find_packages

setup(
    name="scren_tools",
    version="1.1.4",
    packages=find_packages(),
    install_requires=[
        "pyppeteer",
        "pillow"
    ],
    python_requires='>=3.7',
    description="Ultimate full page screenshot library",
    author="Abolfazl",
    url="https://github.com/username/scrt",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
