import os

from codecs import open
from setuptools import setup, find_packages


ROOT_DIR = os.path.abspath(os.path.dirname(__file__))


with open(os.path.join(ROOT_DIR, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='Flask Unchained',
    version='0.1.6',
    description='The better way to build large Flask applications',
    long_description=long_description,
    url='https://github.com/briancappello/flask-unchained',
    author='Brian Cappello',
    license='MIT',

    packages=find_packages(exclude=['docs', 'tests']),
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.6',
    install_requires=[
        'flask>=0.12.2',
        'networkx>=2.1',
    ],
    extras_require={
        'dev': [
            'coverage',
            'pytest',
            'pytest-flask',
            'tox',
        ],
    },

    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    entry_points='''
        [console_scripts]
        flask=flask_unchained.cli:main
        [pytest11]
        flask_unchained=flask_unchained.pytest
    ''',
)
