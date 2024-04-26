# module: `dagrunner.execute_graph`

[Source](../dagrunner/execute_graph.py#L0)

see [dagrunner.utils.logger](dagrunner.utils.logger.md#module_dagrunner_utils_logger)

# class: `ExecuteGraph`

[Source](../dagrunner/execute_graph.py#L159)

see [NodeAwarePlugin](dagrunner.plugin_framework.md#class_nodeawareplugin)

see [ObjectAsStr](dagrunner.utils.md#class_objectasstr)

# dict: `SCHEDULERS`

# class: `SkipBranch`

[Source](../dagrunner/execute_graph.py#L33)

This exception is used to skip a branch of the execution graph.

To be used in combination to one of the multiprocessing schedulers.
In the single-threaded scheduler, Dask executes tasks sequentially, and
exceptions will propagate as they occur, potentially halting the execution of
subsequent tasks.

see [TimeIt](dagrunner.utils.md#class_timeit)

see [function_to_argparse](dagrunner.utils.md#function_function_to_argparse)

# function: `main`

[Source](../dagrunner/execute_graph.py#L257)

Entry point of the program.
Parses command line arguments and executes the graph using the ExecuteGraph class.

# function: `plugin_executor`

[Source](../dagrunner/execute_graph.py#L46)

Executes a plugin function or method with the provided arguments and keyword arguments.

Args:
    *args: Positional arguments to be passed to the plugin function or method.
    call: A tuple containing the callable object or python dot path to one, and its keyword arguments.
    verbose: A boolean indicating whether to print verbose output.
    dry_run: A boolean indicating whether to perform a dry run without executing the plugin.
    common_kwargs: A dictionary of optional keyword arguments to apply to all applicable plugins.
        That is, being passed to the plugin call if such keywords are expected from the plugin.
        This is a useful alternative to global or environment variable usage.
    **node_properties: Node properties.  These will be passed to 'node-aware' plugins.

Returns:
    The result of executing the plugin function or method.

Raises:
    ValueError: If the `call` argument is not provided.

see [visualise_graph](dagrunner.utils.visualisation.md#function_visualise_graph)

