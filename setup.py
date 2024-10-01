from setuptools import setup, find_packages

setup(
    name='my-cli-package',
    version='0.1.0',
    packages=find_packages(exclude=['tests*']),
    install_requires=[
        'click',
    ],
    entry_points={
        'console_scripts': [
            'mycli=my_cli_package.cli:hello',
        ],
    },
    author='Your Name',
    author_email='your.email@example.com',
    description='A simple CLI application',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/my-cli-project',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)