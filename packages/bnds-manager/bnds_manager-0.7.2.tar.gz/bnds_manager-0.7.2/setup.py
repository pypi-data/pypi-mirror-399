import setuptools
import os

VERSION_FILE = os.path.join(os.path.dirname(__file__), 'bnds_manager/_version.py')
version_string = open(VERSION_FILE, 'r').read()

version = version_string.split(' = ')[1][1:-2]

setuptools.setup(
    name="bnds_manager",
    version=version,
    author="Rachel Sumner",
    author_email="r.sumner@qmul.ac.uk",
    description="Python API for managing models and configurations on the BNDS server",
    url="https://github.research.its.qmul.ac.uk/deri-rim/bnds_manager",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['requests', 'simplejson', 'pandas', 'numpy'],
    include_package_data=True
)
