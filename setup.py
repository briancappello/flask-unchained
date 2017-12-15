from setuptools import setup, find_packages


with open('README.md', encoding='utf-8') as f:
    long_description = f.read()


def is_pkg(line):
    return line and not line.startswith(('--', 'git', '#'))


def read_requirements(filename):
    with open(filename, encoding='utf-8') as f:
        return [line for line in f.read().splitlines() if is_pkg(line)]


install_requires = read_requirements('requirements.txt')


setup(
    name='flask-unchained',
    version='0.1.0',
    description='Flask Unchained',
    long_description=long_description,
    url='https://github.com/briancappello/flask-unchained',
    author='Brian Cappello',
    license='MIT',

    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(include=['flask_unchained']),
    install_requires=install_requires,
    include_package_data=True,
    zip_safe=True,
)
