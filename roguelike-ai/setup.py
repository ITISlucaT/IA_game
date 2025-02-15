from setuptools import setup, find_packages

setup(
    name='roguelike-ai',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'pygame',
        'numpy',
        'torch',
        'PyYAML'
    ],
    entry_points={
        'console_scripts': [
            'roguelike=main:main'
        ]
    }
)
