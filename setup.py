from setuptools import setup, find_packages


with open('README.md', encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='Flask-Unchained',
    version='0.9.0',
    description='The quickest and easiest way to build web apps and APIs with Flask',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/briancappello/flask-unchained',
    author='Brian Cappello',
    license='MIT',

    packages=find_packages(exclude=['docs', 'tests']),
    py_modules=['flask_mail'],
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.8',
    install_requires=[
        'blinker>=1.4',
        'click>=8.0.1',
        'flask>=2.0.1',
        'flask_babel>=0.9.4',
        'flask-wtf>=1.0.0',
        'py-meta-utils>=0.7.8',
        'pyterminalsize>=0.1.0',
        'networkx>=2.7.1',
        'werkzeug>=2.0.1',
        'wtforms>=3.0.0',
        'email-validator>=1.1.3',
    ],
    extras_require={
        'admin': [
            'flask-admin>=1.5.8',
        ],
        'api': [
            'apispec>=5.1.1',
            'apispec-webframeworks>=0.5.2',
            'flask-marshmallow>=0.14.0',
            'marshmallow>=3.14.1',
            'marshmallow-sqlalchemy>=0.26.1',
        ],
        'asyncio': [
            'quart>=0.13.1',
        ],
        'celery': [
            'celery>=5.2.1',
            'dill>=0.3.4',
        ],
        'dev': [
            'IPython>=7.24.1',
            'factory-boy',
            'pytest>=4.6.5,<8',
            'pytest-flask>=1.0.0',
        ],
        'docs': [
            'IPython>=7.24.1',
            'sphinx>=4.1.2',
            'sphinx-click>=3.0.1',
            'sphinx-material>=0.0.34',
            'm2r2>=0.3.1',
        ],
        'graphene': [
            'graphql-core>=2.3.1,<3',
            'graphql-relay>=2.0.1,<3',
            'graphql-server-core>=1.2.0,<2',
            'flask-graphql>=2.0',
            'graphene>=2.1.9,<3',
            'graphene-sqlalchemy>=2.2.2,<3',
        ],
        'mail': [
            'beautifulsoup4>=4.9.3',
            'lxml>=4.6.3',
        ],
        'oauth': [
            'Flask-OAuthlib>=0.9.6',
        ],
        'security': [
            'bcrypt>=3.2.0',
            'flask-login>=0.5.0',
            'flask-principal>=0.4.0',
            'itsdangerous>=2.0.1',
            'passlib>=1.7.4',
        ],
        'session': [
            'dill>=0.3.4',
            'flask-session>=0.6.0',
        ],
        'sqlalchemy': [
            'flask-migrate>=3.1.0',
            'flask-sqlalchemy>=3.0,<3.1',
            'flask-sqlalchemy-unchained>=0.8,<0.9',
            'sqlalchemy>=1.4,<2',
            'wtforms_sqlalchemy>=0.4',
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
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    entry_points='''
        [console_scripts]
        flask=flask_unchained.cli:main
        [pytest11]
        flask_unchained=flask_unchained.pytest
    ''',
)
