#!/usr/bin/env python3
"""
Setup script for django-path-tracer package.
"""

from setuptools import setup
import os

# Read the README file
readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
long_description = ""
if os.path.exists(readme_path):
    with open(readme_path, 'r', encoding='utf-8') as f:
        long_description = f.read()

setup(
    name='django-path-tracer',
    version='1.0.0',
    description='Trace Django function calls to their API endpoints',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='HeyMarvin',
    author_email='vishnu@heymarvin.com',
    url='https://github.com/user-focus/talk-to-your-users',
    license='MIT',
    py_modules=['django_path_tracer'],
    python_requires='>=3.8',
    install_requires=[
        # No external dependencies - uses only standard library
    ],
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Framework :: Django',
    ],
    entry_points={
        'console_scripts': [
            'django-path-tracer=django_path_tracer:main',
        ],
    },
)
