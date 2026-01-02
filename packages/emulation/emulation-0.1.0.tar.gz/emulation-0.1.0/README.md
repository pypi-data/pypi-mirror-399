# EMulation

A Python package for creating synthetic cryoEM (cryo-electron microscopy) micrographs.

## Description

EMulation provides tools for generating synthetic cryoEM micrographs, enabling researchers to create realistic simulated electron microscopy images for testing, validation, and algorithm development.

The code heavily borrows from CryoGEM (https://github.com/Cellverse/CryoGEM) and builds on CryoGEM's structure, implementing a new generator and discriminator approaches as well as paired, to some extent, training strategy. 

## Installation

Install EMulation from PyPI:

```bash
pip install emulation
```

Or install from source:

```bash
git clone https://github.com/yourusername/emulation.git
cd emulation
pip install -e .
```