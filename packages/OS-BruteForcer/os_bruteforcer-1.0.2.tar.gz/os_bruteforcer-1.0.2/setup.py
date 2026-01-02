from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='OS-BruteForcer',
    version='1.0.2',
    author='cyb2rS2c',
    author_email='',
    license="MIT",
    description='A Python automation tool for OS detection and login attempts using nmap, hydra, and xfreerdp/sshpass.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/cyb2rS2c/OS_BruteForcer',
    packages=find_packages(),
    install_requires=[
        'colorama',
        'termcolor',
        'pyfiglet',
        'setuptools',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'os-bruteforcer = src.OS_bruteforcer:main',
        ],
    },
    include_package_data=True,
)
