from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='pyprolog',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=required,
    entry_points={},
    author='Rob Sliwa',
    author_email='robjsliwa@example.com',
    description='Prolog implemented in Python',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/robjsliwa/pyprolog',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)
