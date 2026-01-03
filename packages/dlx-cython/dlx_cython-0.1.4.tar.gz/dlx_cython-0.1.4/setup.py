from setuptools import setup, Extension, find_packages
from Cython.Build import cythonize
import numpy

# Read the README file for long description
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "DLX (Dancing Links) implementation in Cython"

extensions = [
    Extension(
        "dlx",
        ["dlx.pyx"],
        include_dirs=[numpy.get_include()],
        extra_compile_args=['-O3'],
    ),
]

setup(
    name='dlx-cython',
    version='0.1.4',
    author='Robert Brooks',
    author_email='robmbrooks@gmail.com',
    description='DLX (Dancing Links) implementation in Cython',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/robmbrooks/dlx',
    project_urls={
        'Bug Reports': 'https://github.com/robmbrooks/dlx/issues',
        'Source': 'https://github.com/robmbrooks/dlx',
        'Documentation': 'https://github.com/robmbrooks/dlx#readme',
    },
    py_modules=['dlxsolver'],
    ext_modules=cythonize(extensions, compiler_directives={
        'language_level': "3",
        'boundscheck': False,
        'wraparound': False,
        'initializedcheck': False,
        'cdivision': True,
    }),
    packages=find_packages(exclude=['tests', 'examples', 'benchmarks']),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Cython',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    install_requires=[
        'numpy>=1.19.0',
    ],
    setup_requires=[
        'cython>=0.29.0',
        'numpy>=1.19.0',
    ],
    extras_require={
        'dev': [
            'pytest>=6.0.0',
            'pytest-cov>=2.0.0',
        ],
    },
    zip_safe=False,
    keywords='dlx dancing-links exact-cover algorithm cython optimization',
)
