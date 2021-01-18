from setuptools import setup, find_packages


with open('README.md', encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='Flask-Unchained',
    version='0.8.1',
    description='The quickest and easiest way to build large web apps and APIs with Flask and SQLAlchemy',
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
        'click>=7.1.2',
        'flask>=1.1.2',
        'flask_babelex>=0.9.4',
        'flask-wtf>=0.14.3',
        'py-meta-utils>=0.7.8',
        'pyterminalsize>=0.1.0',
        'networkx>=2.4',
        'werkzeug>=1.0.1',
        'wtforms>=2.3.3',
        'email-validator>=1.1.2',
    ],
    extras_require={
        'admin': [
            'flask-admin>=1.5.7',
        ],
        'api': [
            'apispec>=3.3.1,<4',
            'flask-marshmallow>=0.14.0',
            'marshmallow>=3.9.1',
            'marshmallow-sqlalchemy>=0.24.1',
        ],
        'asyncio': [
            'quart>=0.13.1',
        ],
        'celery': [
            'celery>=4.4.7',
            'dill>=0.3.3',
        ],
        'dev': [
            'coverage>=4.5.1',
            'IPython>=7.16.0',
            'pytest>=4.6.5',
            'pytest-flask>=1.0.0',
            'tox>=3.5.2',
        ],
        'docs': [
            'IPython>=7.16.0',
            'PyQt5>=5.15.1',
            'qtconsole>=4.7.7',
            'sphinx>=2.4.4,<3',  # m2r needs a new release to support sphinx v3+
            'sphinx-click>=1.4.0',
            'sphinx-material>=0.0.32',
            'm2r>=0.2.1',
        ],
        'graphene': [
            'graphql-core>=2.3.1,<3',
            'graphql-relay>=2.0.1,<3',
            'graphql-server-core>=1.2.0,<2',
            'flask-graphql>=2.0',
            'graphene>=2.1.8,<3',
            'graphene-sqlalchemy>=2.2.2,<3',
        ],
        'mail': [
            'beautifulsoup4>=4.9.3',
            'lxml>=4.6.1',
        ],
        'oauth': [
            'Flask-OAuthlib>=0.9.5',
        ],
        'security': [
            'bcrypt>=3.2.0',
            'flask-login>=0.5.0',
            'flask-principal>=0.4.0',
            'itsdangerous>=1.1.0',
            'passlib>=1.7.4',
        ],
        'session': [
            'dill>=0.3.3',
            'flask-session>=0.3.2',
        ],
        'sqlalchemy': [
            'factory_boy>=2.11.1',
            'flask-migrate>=2.5.3',
            'flask-sqlalchemy-unchained>=0.7.3',
            'sqlalchemy-unchained>=0.11.0',
            'wtforms_sqlalchemy>=0.2',
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
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    entry_points='''
        [console_scripts]
        flask=flask_unchained.cli:main
        [pytest11]
        flask_unchained=flask_unchained.pytest
    ''',
)
