from setuptools import setup
import os
import sys

_here = os.path.abspath(os.path.dirname(__file__))

if sys.version_info[0] < 3:
    with open(os.path.join(_here, 'README.md')) as f:
        long_description = f.read()
else:
    with open(os.path.join(_here, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()

version = {}
with open(os.path.join(_here, 'pictograph', 'version.py')) as f:
    exec(f.read(), version)

setup(
    name='pictograph',
    version=version['__version__'],
    description='Create interconnected compute glyphs',
    long_description='Use compute glyphs to create data processing graph.',
    author='Steve Richardson',
    author_email='steve.richardson@nrl.navy.mil',
    license='',
    packages=[
        'pictograph',
        ],
    install_requires=[
        'numpy',
        ],
    include_package_data=True,
    setup_requires=["pytest-runner"],
    tests_require=["pytest", "pytest-cov"],
    classifiers=[
        'Development Status :: 1 - Development',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3.9'],
    )
