![Python Project](https://img.shields.io/badge/language-Python%20>=3.9-blue?logo=python&logoColor=white)
[![GitHub Tag](https://img.shields.io/github/v/tag/MetOffice/dagrunner)](https://github.com/MetOffice/dagrunner/tags)
[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
![Experimental](https://img.shields.io/badge/status-experimental-orange)
![Static Badge](https://img.shields.io/badge/install-pip-blue)
![PR CI status](https://github.com/MetOffice/dagrunner/actions/workflows/tests.yml/badge.svg)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

# <img src="docs/symbol.svg" alt="dagrunner_icon" width=200px>![](https://placehold.co/600x200/transparent/929292?text=DAGrunner)

DAGrunner serves as a Directed Acyclic Graph (DAG) runner, primarily designed to ensure a clear distinction between a project's graph definition (typically in native networkx format) and its execution method. In essence, DAGrunner offers various schedulers for executing the graph, but it firmly separates these operational concepts from the scientific configuration or recipe, i.e., the graph itself. Consequently, while DAGrunner currently provides convenient scheduling options, it remains adaptable to future changes or alternative solutions, ensuring that the scientific configuration can persist regardless of the technologies or tools employed, whether DAGrunner is utilized or not.

## Documentation

DAGrunner takes advantage of the native markdown rendering support provided by github.  To that end, all documentation of DAGrunner resides in markdown files.

## API

See [DAGrunner API](docs/dagrunner_index.md)

## License/copyright

(C) Crown Copyright, Met Office. All rights reserved.

This file is part of 'DAGrunner' and is released under the BSD 3-Clause license.
See LICENSE in the root of the repository for full licensing details.

## Installation

The package is [pip](https://pip.pypa.io/en/stable/) installable.
```
pip install .
```

(uninstall: `pip uninstall dagrunner`)

This will also make an executable script available to the PATH: `dagrunner-execute-graph`

## Execution of a networkx graph using `dagrunner-execute-graph` script

```
usage: dagrunner-execute-graph [-h] [--scheduler SCHEDULER] [--num-workers NUM_WORKERS] [--profiler-filepath PROFILER_FILEPATH] [--dry-run] [--verbose] networkx-graph
```
see `dagrunner-execute-graph --help` for more information.

## Example DAGRunner usage

See [docs/demo.ipynb](docs/demo.ipynb)

## Processing modules (aka plugins)

DAGrunner concerns itself with graph execution and does not strictly require processing modules (plugins) to take any particular form.  That is, you may or may not choose to use or subclass the plugins provided by DAGrunner.
However, for convenience, DAGrunner does define some plugins which fall into two broad categories, some abstract and some for use as they are.

See [here](docs/dagrunner.plugin_framework.md) for more information.

## Schedulers

The `dagrunner-execute-graph` script exposes a scheduler argument for specifying our preferred scheduler.  DAGRunner provides a layer of abstraction for schedulers.  This enables a range of schedulers to be selected as per requirement.

These range from [dask](https://www.dask.org/), [ray](https://docs.ray.io/en/latest/ray-more-libs/dask-on-ray.html) to our own in-house multiprocessing asynchronous scheduler (built upon the [multiprocessing](https://docs.python.org/3/library/multiprocessing.html) library).  See command help for further details.

## Logging and monitoring

DAGrunner provides a script `dagrunner-logger` for running a TCP server.  This enables logging to function across the network.  Additionally, it will write logs to an sqlite database to aid in realtime monitoring from external tools.
See [logger](docs/dagrunner.utils.logger.md) for more information.
