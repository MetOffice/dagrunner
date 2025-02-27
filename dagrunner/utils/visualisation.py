# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
"""
Module responsible for scheduler independent graph visualisation
"""

import base64
import math
import os
import warnings
import webbrowser
from typing import Iterable, Union

import networkx as nx

from . import as_iterable, in_notebook

# set web component path to relative local file when running pytest
if os.environ.get("PYTEST_VERSION") is not None:
    WEBCOMPONENT_PATH = "../../../visual/mermaid-table-standard.js"
else:
    WEBCOMPONENT_PATH = "https://cdn.jsdelivr.net/gh/MetOffice/dagrunner@vvisual_theme_toggle/visual/mermaid-table-standard.js"


MERMAID_SUBGRAPH_COLORS = [
    "#D4A76A",  # Muted Orange)
    "#A0C4DE",  # Muted Sky Blue)
    "#78B69A",  # Muted Green)
    "#DDD290",  # Muted Yellow)
    "#7E9ACD",  # Muted Blue)
    "#BF8163",  # Muted Vermillion)
    "#B58FA4",  # Muted Reddish Purple)
]


def _as_html(msg):
    """Quick nasty convert text to html, avoid beautiful soup dep."""
    return str(msg).replace(">", "&gt;").replace("<", "&lt;").replace("\n", "<br>")


class HTMLTable:
    TABLE_TEMPLATE = """<table slot="table">
    <thead>{table_header}
    </thead>
    <tbody>{table_cont}
    </tbody>
</table>
"""

    def __init__(self, column_names):
        self._table_cont = ""
        self._table_header = (
            "\n        <tr>"
            + "".join([f"<th>{column_name}</th>" for column_name in column_names])
            + "</tr>"
        )
        self._ncols = len(column_names)

    def add_row(self, *args, id=None):
        tr = ""
        if id is not None:
            tr = f' id="row{id}"'
        self._table_cont += (
            f"\n        <tr{tr}>"
            + "".join([f"<td>{_as_html(arg)}</td>" for arg in args])
            + "</tr>"
        )

    def __str__(self):
        return self.TABLE_TEMPLATE.format(
            table_header=self._table_header, table_cont=self._table_cont
        )


class MermaidGraph:
    MERMAID_TEMPLATE = "---\ntitle: {title}\n---\ngraph TD\n{cont}"
    CARRIAGE_RETURN = "<br>"
    WHITESPACE = "#nbsp;"  # UTF-8
    GTOP = "#gt;"
    LTOP = "#lt;"

    def __init__(self, title=None):
        self._cont = ""
        self._title = title or ""

    def add_raw(self, raw):
        self._cont += f"\n{raw}"

    def add_node(self, nodeid, label=None, tooltip=None, url=None):
        if label:
            label = label.replace("\n", self.CARRIAGE_RETURN)
        self._cont += f'\n{nodeid}(["{label}"])'
        if tooltip:
            # https://mermaid-js.github.io/mermaid/#/flowchart?id=interaction
            tooltip = tooltip.replace("  ", self.WHITESPACE * 2)
            tooltip = tooltip.replace("<", self.LTOP)
            tooltip = tooltip.replace(">", self.GTOP)
            tooltip = tooltip.replace("\n", self.CARRIAGE_RETURN).replace('"', "")
            self._cont += f'\nclick {nodeid} callback "{tooltip}"'
        if url:
            self._cont += f'\nclick {nodeid} "{url}"'

    def add_connection(self, id1, id2):
        self._cont += f"\n{id1} --> {id2}"

    def __str__(self):
        return self.MERMAID_TEMPLATE.format(title=self._title, cont=self._cont)

    def display(self):
        # in jupiter 7.1, we have native markdown support for mermaid
        import notebook
        import requests
        from IPython.display import Image, Markdown, display

        # Mermaid graph definition
        graph = self.__str__()

        notebook_version = tuple(map(int, notebook.__version__.split(".")))
        if notebook_version >= (7, 1) and False:
            # Use native Mermaid rendering in Markdown (doesn't support special
            # characters so disabled for now).
            display(Markdown(f"```mermaid\n{graph}\n```"))
        else:
            # Use the Mermaid API via mermaid.ink to render the graph as an image

            # Encode the graph for use in the Mermaid API
            graphbytes = graph.encode("ascii")
            base64_bytes = base64.b64encode(graphbytes)
            base64_string = base64_bytes.decode("ascii")

            # Fetch the rendered image from the Mermaid API
            image_url = f"https://mermaid.ink/img/{base64_string}"
            response = requests.get(image_url)

            # Display the image directly in the notebook
            if response.status_code == 200:
                display(Image(response.content))
            else:
                print(f"Failed to fetch the image. Status code: {response.status_code}")


class MermaidHTML:
    GRAPH_ENGINE = MermaidGraph
    HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Mermaid diagram lookup</title>
    <script src="{webcomponent_path}" defer></script>
</head>

<body>

<mermaid-table-standard>
<div class="mermaid", slot="mermaid">
{graph}
</div>
{table}
</mermaid-table-standard>

</body>
</html>
"""  # noqa: E501

    def __init__(self, mermaid, table=None):
        self._graph, self._html_table = mermaid, table

    def __str__(self):
        return self.HTML_TEMPLATE.format(
            graph=str(self._graph),
            table=str(self._html_table),
            webcomponent_path=WEBCOMPONENT_PATH,
        )

    def save(self, output_filepath):
        assert os.path.splitext(output_filepath)[-1] in [
            ".html",
        ], "Expecting graph output file extension to be .html"
        with open(output_filepath, "w") as fh:
            fh.write(str(self))


def visualise_graph_matplotlib(
    graph: nx.DiGraph,
    node_info_lookup: dict = None,
    title: str = None,
    output_filepath: str = None,
):
    """
    Visualise a networkx graph using matplotlib.

    Note that this backend is provided as-is and not intended for production use.
    'mermaid' graph is the recommended approach to graph visualisation.

    Args:
    - `graph`: The graph to visualise.
    - `node_info_lookup`: A dictionary mapping nodes to their information.
    - `title`: The title of the visualisation.
    - `output_filepath`: The output filepath to save the visualisation to.
    """
    import matplotlib.pyplot as plt
    from matplotlib.backend_bases import MouseButton

    warnings.warn(
        "This function is deprecated. Use 'mermaid' backend instead.",
        DeprecationWarning,
    )

    pos = nx.spring_layout(graph, seed=42, k=8 / math.sqrt(graph.order()))

    plt.figure()
    plt.title(title)

    # Draw nodes
    nx.draw_networkx_nodes(graph, pos)

    # Get connected components
    components = nx.weakly_connected_components(graph)

    # Define a color palette with more distinct colours
    color_palette = [
        "red",
        "green",
        "blue",
        "orange",
        "purple",
        "yellow",
        "cyan",
        "magenta",
    ]

    # Draw each disconnected graph component with a different color from the palette
    for i, component in enumerate(components):
        color = color_palette[i % len(color_palette)]
        nx.draw_networkx_edges(
            graph,
            pos,
            edgelist=[
                (u, v) for u, v in graph.edges() if u in component and v in component
            ],
            edge_color=color,
            arrowstyle="->",
            arrowsize=20,
        )

        # Highlight starting and termination nodes
        sources = {node for node in component if graph.in_degree(node) == 0}
        targets = {node for node in component if graph.out_degree(node) == 0}
        nx.draw_networkx_nodes(
            graph, pos, nodelist=sources, node_color="green", node_size=200
        )
        nx.draw_networkx_nodes(
            graph, pos, nodelist=targets, node_color="red", node_size=200
        )

    # Draw labels
    nx.draw_networkx_labels(graph, pos, font_size=6, font_color="black")

    # Capture clicks on nodes
    def on_click(event):
        if event.button is MouseButton.LEFT and event.inaxes:
            x, y = event.xdata, event.ydata
            for node, (nx, ny) in pos.items():
                if (x - nx) ** 2 + (y - ny) ** 2 < 0.05:  # Click radius threshold
                    print(f"Node clicked: {node}")
                    if node_info_lookup:
                        print(node_info_lookup[node])
                    else:
                        print(graph.nodes[node])
                    break

    # Connect the event handler
    fig = plt.gcf()
    fig.canvas.mpl_connect("button_press_event", on_click)

    if output_filepath:
        plt.savefig(output_filepath)
    else:
        plt.show()


def _gen_label(node_id, node, label_by):
    label = f"{node_id}"
    if label_by:
        for key in label_by:
            if (val := getattr(node, key)) is not None:
                label += f"\n{key}: {val}"
    else:
        label += f"\n{str(node)}"
    return label


def _add_node(
    node,
    mermaid,
    table,
    node_id,
    node_target_id_map,
    node_data,
    label_by,
    tooltip_data=None,
):
    table_delim = "; "  # \n could be useful here
    if node not in node_target_id_map:
        node_target_id_map[node] = node_id
        label = _gen_label(node_id, node, label_by)
        tt_data = tooltip_data if tooltip_data is not None else node_data
        tooltip = [f"{key}: {repr(val)}" for key, val in tt_data.items()]
        info = table_delim.join([repr(val) for val in as_iterable(node_data)])
        mermaid.add_node(
            node_id,
            label=label,
            tooltip="\n".join(tooltip),
        )
        if tooltip_data:
            table.add_row(node_id, node, table_delim.join(tooltip), info, id=node_id)
        else:
            table.add_row(node_id, node, info, id=node_id)
        node_id += 1
    return node_id


def visualise_graph_mermaid(
    graph: nx.DiGraph,
    node_data_lookup: dict = None,
    node_tooltip_lookup: dict = None,
    title: str = None,
    output_filepath: str = None,
    group_by: Union[str, Iterable[str]] = None,
    label_by: Union[str, Iterable[str]] = None,
):
    """
    Visualise a networkx graph using mermaid.

    Args:
    - `graph`: The graph to visualise.
    - `node_info_lookup`: A dictionary mapping nodes to their information.
    - `title`: The title of the visualisation.
    - `output_filepath`: The output filepath to save the visualisation to.
    - `group_by`: One or more property to group nodes by (i.e.
      [subgraph](https://mermaid-js.github.io/mermaid/#/subgraph)).
    - `label_by`: One or more property to label visualisation nodes by.
    """
    mermaid = MermaidGraph(title=title or "")
    if node_tooltip_lookup:
        table = HTMLTable(["id", "node", "tooltip", "info"])
    else:
        table = HTMLTable(["id", "node", "info"])

    label_by = as_iterable(label_by)
    group_by = as_iterable(group_by)

    node_target_id_map = {}
    node_id = 0
    nodes = graph.nodes

    if group_by:
        nodes = sorted(
            graph.nodes,
            key=lambda node: [getattr(node, key, "") or "" for key in group_by],
        )

    curr_subgraphs = None
    depth = 0
    for target in nodes:
        if group_by:
            subgraphs_raw = [getattr(target, key) for key in group_by]
            subgraphs = list(filter(None, subgraphs_raw))

            # determining whether subgraphing remains the same
            if curr_subgraphs is not None:
                len_min = min(len(curr_subgraphs), len(subgraphs))
                diff_ind = len_min
                for ind in range(len_min):
                    if curr_subgraphs[ind] != subgraphs[ind]:
                        diff_ind = ind
                        break
                indent_chng = max(0, len(curr_subgraphs) - len(subgraphs)) + (
                    len_min - diff_ind
                )
                for _ in range(indent_chng):
                    mermaid.add_raw("end")

            gen_subgraph = False
            for subg_ind, subgraph in enumerate(subgraphs):
                if gen_subgraph is False and curr_subgraphs is not None:
                    if (
                        len(curr_subgraphs) > subg_ind
                        and curr_subgraphs[subg_ind] == subgraph
                    ):
                        # same subgraph so don't redefine it
                        continue
                gen_subgraph = True

                # subgraph ID is a concatenation of all subgraph IDs within its
                # hierarchy.
                subg_id = "_".join(
                    map(lambda x: x.replace(" ", "_"), subgraphs[: subg_ind + 1])
                )
                depth = len(subgraphs[: subg_ind + 1])
                colour_index = subgraphs_raw.index(subgraph) - 1
                if colour_index >= 0:
                    colour = MERMAID_SUBGRAPH_COLORS[
                        colour_index % len(MERMAID_SUBGRAPH_COLORS)
                    ]
                    mermaid.add_raw(f"style {subg_id} fill:{colour}")
                mermaid.add_raw(f"subgraph {subg_id}[{subgraph}]")
            curr_subgraphs = subgraphs

        if node_data_lookup:
            node_data = node_data_lookup[target]
        else:
            node_data = graph.nodes[target]

        tooltip_data = None
        if node_tooltip_lookup is not None:
            tooltip_data = node_tooltip_lookup[target]

        node_id = _add_node(
            target,
            mermaid,
            table,
            node_id,
            node_target_id_map,
            node_data,
            label_by,
            tooltip_data=tooltip_data,
        )
    if group_by and depth > 0:
        for _ in range(depth):
            mermaid.add_raw("end")

    for target in nodes:
        for pred in graph.predecessors(target):
            mermaid.add_connection(node_target_id_map[pred], node_target_id_map[target])

    if output_filepath:
        MermaidHTML(mermaid, table).save(output_filepath)
    else:
        if in_notebook():
            mermaid.display()
        else:
            import tempfile

            with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
                MermaidHTML(mermaid, table).save(f.name)
                webbrowser.open(f.name)
