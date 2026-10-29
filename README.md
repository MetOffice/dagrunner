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

Though you can execute your graphs by interacting with the DAGrunner library within your interactive Python shell, typically it is assumed to be more useful to utilise the script provided:
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

## Controlling graph execution

Controlling graph execution can broadly be divided into two categories: defining what should be executed before runtime, and controlling how execution proceeds at runtime.

The first is achieved by passing DAGrunner a graph factory, along with any arguments supported by that factory. The graph factory is a project-defined callable that accepts these arguments and returns a graph for execution. This approach intentionally decouples DAGrunner from graph ownership and construction. Rather than imposing a particular mechanism for building graphs, DAGrunner delegates this responsibility to the project itself. As a result, projects are free to define their own graph-construction interfaces, configuration parameters, or user-facing controls. DAGrunner's only requirement is that, when invoked with the supplied arguments, the graph factory returns a valid NetworkX graph.

A common use case is for the graph factory to expose parameters that allow it to return only a subset of the full graph, enabling selective execution of particular workflows or graph sections.

The second category concerns runtime control of graph execution. This is typically achieved through applications that perform specific functions, such as polling for data. DAGrunner already provides a number of such applications, but users can also develop their own applications that emit DAGrunner events. These events can influence the execution of downstream nodes, for example by skipping individual nodes or entire branches of the graph. Such behaviour is propagated through descendant nodes, allowing execution paths to be dynamically adjusted as the workflow runs.

For further details, see the [events](docs/_build/dagrunner.events.md) documentation.

## Logging and monitoring

DAGrunner provides a script `dagrunner-logger` for running a TCP server.  This enables logging to function across the network.  Additionally, it will write logs to an sqlite database to aid in realtime monitoring from external tools.
Terminate it with Ctrl-C (`SIGINT`) or `SIGTERM` to close the server and clean up its SQLite logging handler.
Shutdown finishes in-progress logging and SQLite writes and drains complete records already available on the sockets, without waiting for clients to disconnect. Incomplete records requiring more client data are discarded.
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