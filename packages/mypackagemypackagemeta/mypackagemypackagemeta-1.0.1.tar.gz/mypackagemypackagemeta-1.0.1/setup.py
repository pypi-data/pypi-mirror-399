from setuptools import find_packages, setup

setup(
    name="mypackagemypackagemeta",
    version="1.0.1",
    author="Python learner",
    author_email="hestudio@hestudio.org",
    description="A sample Python package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "numpy>=1.19.0",
    ],
)
