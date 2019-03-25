from setuptools import setup, find_packages


with open('README.md', encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='Flask-Unchained',
    version='0.7.5',
    description='The best way to build Flask apps',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/briancappello/flask-unchained',
    author='Brian Cappello',
    license='MIT',

    packages=find_packages(exclude=['docs', 'tests']),
    py_modules=['flask_mail'],
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.6',
    install_requires=[
        'blinker>=1.4',
        'click>=7.0',
        'flask>=1.0.2',
        'flask_babelex>=0.9.3',
        'flask-wtf>=0.14.2',
        'py-meta-utils>=0.7.5',
        'networkx>=2.1',
    ],
    extras_require={
        'admin': [
            'flask-admin>=1.5.3',
            'sqlalchemy<1.3',
        ],
        'api': [
            'apispec>=0.39.0',
            'flask-marshmallow>=0.9.0',
            'marshmallow>=2.16.1,<3.0',
            'marshmallow-sqlalchemy>=0.15,<0.16',
        ],
        'celery': [
            'celery>=4.2.1',
            'dill>=0.2.8.2',
        ],
        'dev': [
            'coverage>=4.5.1',
            'factory_boy>=2.11.1',
            'IPython>=7.1.1',
            'm2r>=0.2.1',
            'mock>=2.0.0',
            'pytest>=3.9.3',
            'pytest-flask>=0.14.0',
            'tox>=3.5.2',
        ],
        'docs': [
            'IPython>=7.1.1',
            'PyQt5>=5.11.2',
            'qtconsole>=4.4.0',
            'sphinx>=1.8.1',
            'sphinx-autobuild>=0.7.1',
            'sphinx-click>=1.4.0',
            'sphinx-rtd-theme>=0.4.2',
        ],
        'graphene': [
            'flask-graphql>=2.0',
            'graphene>=2.1.3',
            'graphene-sqlalchemy>=2.1.0',
        ],
        'mail': [
            'beautifulsoup4>=4.6.3',
            'lxml>=4.2.4',
        ],
        'oauth': [
            'Flask-OAuthlib>=0.9.5',
        ],
        'security': [
            'bcrypt>=3.1.4',
            'flask-login>=0.4.1',
            'flask-principal>=0.4.0',
            'itsdangerous>=1.1.0',
            'passlib>=1.7.1',
        ],
        'session': [
            'dill>=0.2.8.2',
            'flask-session>=0.3.1',
        ],
        'sqlalchemy': [
            'flask-migrate>=2.2.1',
            'flask-sqlalchemy-unchained>=0.7.1',
            'sqlalchemy-unchained>=0.7.1',
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
