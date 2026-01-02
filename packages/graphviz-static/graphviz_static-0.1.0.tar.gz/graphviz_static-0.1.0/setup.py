from setuptools import setup, find_packages

setup(
    name="graphviz-static",
    version="0.1.0",
    packages=find_packages(),
    package_data={
        'graphviz_static': ['bin/**/*'],
    },
    include_package_data=True,
    install_requires=[],
    author="Hvd/tbtn123/toibithieunang123",
    description="A Graphviz static wrapper for Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/tbtn123/graphviz-static",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.6",
)
