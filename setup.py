from setuptools import setup, find_packages

from rapid import __version__

setup(
    name='rapid',
    version=__version__,
    packages=find_packages(),
    scripts=[
    ],
    package_data={
    },
    install_requires=[
    ],
    description='Routine Automation of Pipelines for Illumina Data',
    url='https://github.com/BCCDC-PHL/rapid',
    author='Dan Fornika',
    author_email='dan.fornika@bccdc.ca',
    entry_points="""
    [console_scripts]
    rapid-run = rapid.run:main
    """,
    include_package_data=True,
    keywords=[],
    zip_safe=False,
)
