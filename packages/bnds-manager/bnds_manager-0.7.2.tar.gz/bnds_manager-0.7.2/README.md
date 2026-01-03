# bnds_manager (v0.7.0)

bnds_manager facilitates the uploading, downloading and updating of models and interfaces on the BNDS server for staff users. The models can be in either .cmpx or .json format based on the format used in AgenaRisk, while the interfaces are a custom .json file. For information on how to create these files please see the bnds manager [wiki](https://github.research.its.qmul.ac.uk/deri-rim/bnds_manager/wiki).

## Installation

We recommended creating a Python virtual environment (for example with conda) in order to install the relevant packages. Detailed instructions for installing Git, creating environments and downloading packages can be found on the [installation](https://github.research.its.qmul.ac.uk/deri-rim/bnds_manager/wiki/1.-Installation) page in the repository [wiki](https://github.research.its.qmul.ac.uk/deri-rim/bnds_manager/wiki).

Once the virtual environment is activated you can use PIP and Git to install the package using the command

```console
$ pip install git+https://github.research.its.qmul.ac.uk/deri-rim/bnds_manager
```

Alternatively you can download the source code and copy to a relevant directory and type

```console
$ pip install <path-to-directory>
```

or, it may be required that you navigate to the relevant directory and type

```console
$ pip install -e .
```

## Usage

The [quick start](https://github.research.its.qmul.ac.uk/deri-rim/bnds_manager/wiki/2.-Quick-Start) guide will show you how to upload a cmpx model and associated interface to the server.

The [wiki](https://github.research.its.qmul.ac.uk/deri-rim/bnds_manager/wiki) explains all the features of the bnds_manager package.
