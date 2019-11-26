from setuptools import setup


setup(
    name='grow-ext-mondayvc',
    version='1.0.0',
    license='MIT',
    author='Grow SDK Authors',
    author_email='hello@grow.io',
    packages=[
        'mondayvc',
    ],
    install_requires = [
        'bleach',
    ],
)
