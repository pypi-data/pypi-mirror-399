from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='threshopt',
    version='1.1.0',  # allineata al pyproject.toml
    packages=find_packages(include=['threshopt', 'threshopt.*']),
    install_requires=[
        'scikit-learn',
        'matplotlib',
        'numpy',
    ],
    author='Salvatore Zizzi',
    author_email='salvo.zizzi@gmail.com', 
    description='Automatic threshold optimization for binary and multiclass classifiers.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/salvo-zizzi/threshopt', 
    license='Apache 2.0',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.7',
)

