# py3dic

Author: Nikolaos Papadakis

This is a repository for the materials lab at HMU.

documentation is (will be) in the github pages for [py3dic](https://npapnet.github.io/py3dic/).

It contains a number of utilities for the easier (and verified) calcualation of properties from the tests that are normally carried out. 

It contains:
- Tensile testing with the Imada MX2 universal testing machine
  - a quick utility based on a matplotlib window
  - a tk mvc controller window with more capabilities
- DIC processing for tensile testing.
  - batch processing
  - rolling gui (incomplete)
  - types of strain:
    - true strain
    - engineering strain (cauchy)
  - interpolation:
    - linear
    - cubic
    - spline
    - raw
  - output images
    - displacement
    - markers
    - grid
    - strain map (not complete)

## Quickstart: Entry points

For simplicity, use the following commands (After installation) to open up the different tools:

| Command line           | Description                                               |
| ---------------------- | --------------------------------------------------------- |
| `tk_dic_analysis`      | GUI for batch processing of DIC data                      |
| `tk_merge_dic`         | GUI for merging data of Universal Tensile Testing and DIC |
| `tk_dic_viewer`        | GUI for strain map processing of DIC data                 |
| dic_strainmaps         | GUI for generating strain maps                            |
| py3dic-jinan-converter | cli tool for converting jinan data to csv                 |


# installation

cd to the directory and execute

> python setup.py install
> python setup.py develop

or (when loaded to pypi)

> pip install py3dic 

to use it import:

> import py3dic as mlt

#  Installation procedure using Conda

## creating a new environment (recommended)

This is the recommended method.

```bash
> conda create -n materialslab python=3
> conda activate materialslab 

```

Alternatively *if you are running low on space on a SSD * drive you can use the prefix option (**IMPORTANT:** read through the following [StackOverflow Question: how to specify new environment location for conda create](https://stackoverflow.com/questions/37926940/how-to-specify-new-environment-location-for-conda-create))


## Install dependencies

Activate the new conda environment and install the following:

```bash
> conda activate materialslab
> conda install opencv numpy scipy
> conda install matplotlib  pandas seaborn
> conda install ipython jupyter
> conda install openpyxl
```


## Install py3dic package.

### from source

Clone the repository from online to <py3dic>.

Change directory into **<py3dic>/pypkg/**

> cd ./pypkg

Install the package locally:

> python setup.py install

### from pypi (not yet implemented)

This will be simpler but not yet implemented

```bash
> pip install py3dic
```
