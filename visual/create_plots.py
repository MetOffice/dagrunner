#!/usr/bin/env python3
# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
"""
Script for creating suite plots based on graph configurations and plot settings.
"""

import argparse
import inspect
import json
import os
import shutil
import warnings
from html import escape
from pathlib import Path

from dagrunner.execute_graph import get_networkx
from dagrunner.utils import function_to_argparse_parse_args
from dagrunner.utils.networkx import (
    collapse_graph,
    visualisation,
)

SCRIPT_DIR = Path(__file__).resolve().parent


def _get_name(callable, call_args):
    config_name = []
    for name, param in inspect.signature(callable).parameters.items():
        # if param is a positional argument and not a keyword argument
        if param.kind in (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
        ):
            config_name += [call_args[name]]
        else:
            config_name += [f"{name}_{call_args[name]}"]
    return "_".join(config_name)


def gen_script(pattern, root_link_text=None):
    """
    Generate a script for handling subgraph clicks in the HTML.

    Args:
        pattern: The pattern to match subgraph clicks against.
            Takes a string or regular expression pattern to match subgraph
            clicks against.
        root_link_text: Optional text for the root link in the top-left corner
            of the component.
            If not provided, no root link will be added.

    Returns:
        The generated script as a string.
    """
    script = """
<script>
    document.addEventListener("DOMContentLoaded", () => {{
        const component = document.querySelector("body > mermaid-table-standard");
        if (!component) return;
""".format()

    if root_link_text:
        script += """
        component.upsertTopLeftLink({{
            id: "graph-link",
            href: "index.html",
            textContent: "{text}"
        }});
""".format(text=root_link_text)

    script += """
        const pattern = {pattern};;
        bindSubgraphClicks((text) => {{
            component.upsertTopLeftLink({{
                id: "node-link",
                href: `${{text}}.html`,
                textContent: `${{text}}`
            }});
        }}, pattern);
    }});
</script>
""".format(pattern=pattern)
    return script


def find_nodes_and_neighbors(graph, detail, detail_by):
    """Find nodes matching the detail and their neighbors.

    Args:
        graph: The graph to search.
        detail: The value to match.
        detail_by: The node attribute to match against.

    Returns:
        A tuple of (detail_nodes, neighbour_nodes) where detail_nodes are the
        nodes matching the detail,
        and neighbour_nodes are their neighbors excluding the detail_nodes themselves.
    """
    detail_nodes = {n for n in graph.nodes if getattr(n, detail_by) == detail}
    res_nodes = set([])

    for node in detail_nodes:
        res_nodes.update(set(graph.predecessors(node)))
        res_nodes.update(set(graph.successors(node)))
    return detail_nodes, res_nodes - detail_nodes


def insert_into_html(html_file, content, matching):
    """
    Insert content into an HTML file before a line matching a specific string.

    Args:
        html_file: The path to the HTML file.
        content: The content to insert.
        matching: The string to match for insertion point.
    """
    with open(html_file, "r") as f:
        html = f.read()

    if content in html:
        print(f"{content} already in {html_file}, skipping insertion.")
        return

    # Insert content before line including matching
    lines = html.splitlines()
    for line in lines:
        if matching in line:
            lines.insert(lines.index(line), content)
            break

    with open(html_file, "w") as f:
        f.write("\n".join(lines))


def load_plot_config(filename):
    """
    Load the plot configuration from a JSON file.

    Takes the following structure:
        {
            "index_title": "<title>",
            "detail_by": "<attribute_name>",
            "level1": {
                "collapse_properties": [...],
                "label_by": "<attribute_name>",
                "group_by": "<attribute_name>"
            },
            "level2": {
                "collapse_properties": [...],
                "label_by": "<attribute_name>",
                "group_by": "<attribute_name>"
            }
        }

    Args:
        filename: The path to the JSON configuration file.

    Returns:
        The loaded configuration as a dictionary.
    """
    try:
        with open(filename) as config_file:
            config = json.load(config_file)
    except (OSError, ValueError) as error:
        raise argparse.ArgumentTypeError(str(error)) from error
    return config


def create_plots(
    networkx_graph: str,
    networkx_graph_kwargs: dict = None,
    output_root: str = None,
    override_existing: bool = False,
    plot_config_filepath: str = None,
    webcomponent: str = None,
):
    """
    Create plots for the given configuration names.

    Will generate visualizations for each configuration name based on the provided plot
    configuration by collapsing the graph according to the specified properties and
    generating two levels of visualizations:
                - Level 1: Collapses the graph according to the properties specified in
                    `level1` of the plot configuration.
                - Level 2: Collapses the graph according to the properties specified in
                    `level2` of the plot configuration.

    The _index.html file is copied and used as the configuration selection page.
    DAGrunner is used to generate the visualizations for each configuration based
    on the collapsed graph.

    Args:
        networkx_graph: A networkx graph; dot path to a networkx graph or callable
            that returns one (str); tuple representing (edges, nodes) or callable
            object that returns a networkx.
        networkx_graph_kwargs: Optional keyword arguments to pass when creating
            the networkx graph.
        output_root: The root directory for output files. If not specified,
            defaults to the current working directory.  Optional.
        override_existing: Whether to override existing files.  Optional.
        plot_config_filepath: The file path to the plot configuration.
        webcomponent: Optional local DAGrunner JavaScript component to bundle
            with the plots.
    """
    networkx_graph = get_networkx(networkx_graph)
    networkx_graph_kwargs = networkx_graph_kwargs or {}
    if not output_root:
        output_root = Path(os.getcwd())

    plot_config = load_plot_config(plot_config_filepath) if plot_config_filepath else {}
    detail_by = plot_config["detail_by"]
    level1_config = plot_config.get("level1", {})
    level2_config = plot_config.get("level2", {})
    index_title = plot_config.get("index_title", "")
    output_root = Path(output_root).resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    root_index = output_root / "index.html"
    if webcomponent:
        shutil.copyfile(
            Path(webcomponent).resolve(), output_root / "mermaid-table-standard.js"
        )
        visualisation.WEBCOMPONENT_PATH = "../mermaid-table-standard.js"

    if not root_index.exists():
        template = (SCRIPT_DIR / "_index.html").read_text()
        root_index.write_text(
            template.replace('"__INDEX_TITLE__"', json.dumps(escape(index_title)))
        )
    elif os.path.exists(root_index):
        warnings.warn(f"{root_index} already exists already.")

    os.chdir(output_root)

    config_name = _get_name(networkx_graph, networkx_graph_kwargs) or "graph"
    print(f"Configuration name: {config_name}")

    config_index = Path(config_name) / "index.html"
    if override_existing:
        shutil.rmtree(config_index.parent, ignore_errors=True)
    config_index.parent.mkdir(parents=True, exist_ok=True)

    if not override_existing and config_index.exists():
        warnings.warn(
            f"{config_index} already exists and will not be overwritten.  "
            "Please remove or specify the --force option to overwrite existing "
            "files.  Skipping generation for this configuration."
        )
        exit(0)

    # Add link to the configuration selection page
    insert_into_html(
        root_index,
        f'<option value="{config_index}">{config_name}</option>',
        "</select>",
    )

    graph = (
        networkx_graph(**networkx_graph_kwargs)
        if callable(networkx_graph)
        else networkx_graph
    )
    if isinstance(graph, tuple):
        graph = graph[0]

    collapse_properties = level1_config["collapse_properties"]
    print(f"Collapsing {config_name} along {collapse_properties}")
    collapsed_graph, node_data_lookup, node_collapsed_lookup = collapse_graph(
        graph, collapse_properties=collapse_properties, collapsed_data_summary=True
    )
    print(
        f"Generating visualisation for {config_name}, "
        f"collapsed along: {collapse_properties}"
    )
    visualisation.visualise_graph_mermaid(
        collapsed_graph,
        title=config_name,
        output_filepath=config_index,
        node_data_lookup=node_data_lookup,
        node_tooltip_lookup=node_collapsed_lookup,
        label_by=level1_config["label_by"],
        group_by=level1_config.get("group_by", ""),
    )

    # Add links to node labels, linking to the uncollapsed graph files
    insert_into_html(
        config_index, gen_script(rf"/{detail_by}:\s*([\w-]+)/i"), "</body>"
    )

    print(f"Generated {str(config_index)}")

    # Generate visualisation for each 'detail_by'
    collapse_properties = level2_config["collapse_properties"]
    print(f"Collapsing {config_name} along {collapse_properties}")
    (
        collapsed_graph_lt,
        node_data_lookup_lt,
        node_collapsed_lookup_lt,
    ) = collapse_graph(graph, collapse_properties=collapse_properties)

    details = set(getattr(node, detail_by) for node in collapsed_graph.nodes)
    for detail in details:
        title = f"{detail}"
        print(
            f"Generating visualisation for {config_name}, {detail_by}:{detail}, "
            f"collapsed along: {collapse_properties}"
        )
        detail_graph = collapsed_graph_lt.copy()

        detail_nodes, dep_nodes = find_nodes_and_neighbors(
            detail_graph, detail, detail_by
        )
        detail_graph.remove_nodes_from(
            (set(detail_graph.nodes) - detail_nodes) - dep_nodes
        )

        visualisation.visualise_graph_mermaid(
            detail_graph,
            title=title,
            output_filepath=config_index.parent / f"{title}.html",
            node_data_lookup=node_data_lookup_lt,
            node_tooltip_lookup=node_collapsed_lookup_lt,
            label_by=level2_config["label_by"],
            group_by=level2_config.get("group_by", ""),
        )

        matching = "|".join(
            [
                getattr(node, detail_by)
                for node in dep_nodes
                if getattr(node, detail_by) is not None
            ]
        )
        # Link node labels to other uncollapsed graph files
        insert_into_html(
            config_index.parent / f"{title}.html",
            gen_script(f"/({matching})/i", config_name),
            "</body>",
        )


def main(*args):
    args, kwargs = function_to_argparse_parse_args(create_plots)
    create_plots(**args, **kwargs)


if __name__ == "__main__":
    main()
