![Python Project](https://img.shields.io/badge/language-Python%20>=3.9-blue?logo=python&logoColor=white)
[![GitHub Tag](https://img.shields.io/github/v/tag/MetOffice/dagrunner)](https://github.com/MetOffice/dagrunner/tags)
[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
![Experimental](https://img.shields.io/badge/status-experimental-orange)
![Static Badge](https://img.shields.io/badge/install-pip-blue)
![PR CI status](https://github.com/MetOffice/dagrunner/actions/workflows/tests.yml/badge.svg)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

<img src="docs/logo_wtitle.svg" alt="dagrunner_icon" width=400px>

DAGrunner provides an abstraction layer between an execution Directed Acyclic Graph (DAG) and the scheduler used to run it. Rather than coupling workflows to scheduler-specific APIs and execution models, DAGrunner represents execution graphs as [NetworkX](https://networkx.org/en/) graphs that can be executed using any supported back end, such as [Dask](https://www.dask.org/) or [Ray](https://docs.ray.io/en/latest/index.html). This separation of concerns allows scheduling technologies to evolve or be replaced without requiring changes to the workflow graph, making the approach valuable regardless of future orchestration frameworks or execution technologies.

Beyond its core abstraction layer, DAGrunner provides scheduler-agnostic tooling for graph visualisation, logging, monitoring, and fault handling, including support for recovery from execution failures. It also includes abstract classes for common application patterns such as data loading and polling, and standardises event handling during graph execution. Together, these capabilities simplify application development, provide a consistent user experience across schedulers, and avoid scheduler-specific implementations.

## Documentation

DAGrunner documentation is written in markdown so it renders natively on GitHub and in popular IDEs. Reference documentation is generated from the codebase as markdown via [docs/gen_docs](docs/gen_docs). These generated docs are built automatically with continuous integration and should not be included in code changes.

## API reference

See [DAGrunner API](docs/_build/dagrunner_index.md)

## Installation

The package is [pip](https://pip.pypa.io/en/stable/) installable.
```
pip install .
```

(uninstall: `pip uninstall dagrunner`)

This will also make an executable script available to the PATH: `dagrunner-execute-graph`

## Execution of a networkx graph using the `dagrunner-execute-graph` script

Thought you can execute your graphs by interacting with the DAGrunner library within your interactive Python shell, typically it is assumed to be more useful to utilise the script provided:
```
usage: dagrunner-execute-graph [-h] [--scheduler SCHEDULER] [--num-workers NUM_WORKERS] [--profiler-filepath PROFILER_FILEPATH] [--dry-run] [--verbose] networkx-graph
```
see `dagrunner-execute-graph --help` for more information.

## Example DAGrunner usage

See [docs/demo.ipynb](docs/demo.ipynb)

Also, take a look at the [FAQ](FAQ.md#what-do-i-need-to-execute-my-graph-with-dagrunner) for a quick-start example.

## Processing modules (aka applications)

DAGrunner concerns itself with graph execution and does not strictly require node execution to take any particular form.  That is, you may or may not choose to use or subclass the plugins provided by DAGrunner.
However, for convenience, DAGrunner does define some classes which fall into two broad categories, some abstract and some for use as they are.

See [here](docs/_build/dagrunner.plugin_framework.md) for more information.

## Schedulers

The `dagrunner-execute-graph` script exposes a scheduler argument for specifying our preferred scheduler.  DAGrunner provides a layer of abstraction for schedulers.  This enables a range of schedulers to be selected as per requirement.

These range from [dask](https://www.dask.org/), [ray](https://docs.ray.io/en/latest/ray-more-libs/dask-on-ray.html) to our own in-house multiprocessing asynchronous scheduler (built upon the [multiprocessing](https://docs.python.org/3/library/multiprocessing.html) library).  See command help for further details.

## Logging and monitoring

DAGrunner provides a script `dagrunner-logger` for running a TCP server.  This enables logging to function across the network.  Additionally, it will write logs to an sqlite database to aid in realtime monitoring from external tools.
See [logger](docs/_build/dagrunner.utils.logger.md) for more information.

## FAQ

See [here](FAQ.md)

## Logo

Colour: | B&W: | Title:
--- | --- | ---
<img src="docs/logo.svg" alt="dagrunner_icon" height=90px> | <img src="docs/logo_bw.svg" alt="dagrunner_icon" height=90px> | <img src="docs/logo_title.svg" alt="dagrunner_icon" width=200px>

Colour + title: | B&W + title:
--- | ---
<img src="docs/logo_wtitle.svg" alt="dagrunner_icon" height=90px> | <img src="docs/logo_bw_wtitle.svg" alt="dagrunner_icon" height=90px>

## License/copyright

(C) Crown Copyright, Met Office. All rights reserved.

This file is part of 'DAGrunner' and is released under the BSD 3-Clause license.
See LICENSE in the root of the repository for full licensing details.