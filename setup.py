from setuptools import setup, find_packages


with open('README.md', encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='Flask Unchained',
    version='0.4.0',
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
        'blinker>=1.4',
        'flask>=0.12.2',
        'flask_babelex>=0.9.3',
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
