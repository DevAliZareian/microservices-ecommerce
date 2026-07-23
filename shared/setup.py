from setuptools import setup, find_packages
import os

# Get the directory where setup.py is located
setup_dir = os.path.dirname(os.path.abspath(__file__))

setup(
    name='ecommerce-shared',
    version='1.0.0',
    packages=find_packages(where=setup_dir),
    install_requires=[
        'django>=4.2',
        'djangorestframework>=3.14',
        'httpx>=0.24',
    ],
    description='Shared utilities for e-commerce microservices',
)
