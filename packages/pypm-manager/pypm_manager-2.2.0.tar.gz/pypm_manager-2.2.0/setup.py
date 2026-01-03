from setuptools import setup, find_packages
from pathlib import Path

# Read the long description from README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name='pypm-manager',
    version='2.2.0',
    author='Avishek',
    author_email='avishek8136@github.com',
    description='Python package manager with true version isolation - multiple package versions coexist without conflicts',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Avishek8136/pypm',
    project_urls={
        'Documentation': 'https://github.com/Avishek8136/pypm#readme',
        'Source': 'https://github.com/Avishek8136/pypm',
        'Issues': 'https://github.com/Avishek8136/pypm/issues',
    },
    packages=find_packages(exclude=['tests', 'examples']),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Software Distribution',
    ],
    keywords='package-manager environment dependencies storage efficiency',
    python_requires='>=3.7',
    install_requires=[
        # No external dependencies - uses only Python standard library!
    ],
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-cov>=4.1.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'pypm=pypm.cli:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
