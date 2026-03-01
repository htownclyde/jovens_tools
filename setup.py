from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='jovens_tools',
    version='0.0.1',
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'jovens_tools = jovens_tools.__main__:main'
        ]
    }
)