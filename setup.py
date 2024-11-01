"""A setuptools based setup module."""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open

setup(
    name='ergpyspedas',
    version='0.0',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=['pyspedas>=1.2.8', 'vtk>=9.2.2', 'pyside6>=6.4.1'],
    python_requires='>=3.7',
    include_package_data=True,
)
