import os
import versioneer

from codecs import open
from setuptools import setup, find_packages


ROOT_DIR = os.path.abspath(os.path.dirname(__file__))


with open(os.path.join(ROOT_DIR, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


def read_requirements(filename):
    def is_pkg(line):
        return line and not line.startswith(('--', 'git', '#'))

    with open(os.path.join(ROOT_DIR, filename), encoding='utf-8') as f:
        return [line for line in f.read().splitlines() if is_pkg(line)]


setup(
    name='Flask Unchained',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='Flask Unchained',
    long_description=long_description,
    url='https://github.com/briancappello/flask-unchained',
    author='Brian Cappello',
    license='MIT',

    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(exclude=['tests']),
    install_requires=read_requirements('requirements.txt'),
    python_requires='>=3.6',
    extras_require={
        'test': ['coverage', 'pytest', 'pytest-flask'],
    },
    include_package_data=True,
    zip_safe=False,
    entry_points='''
        [console_scripts]
        flask=manage:main
    ''',
)
