# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'pp_systems_framework' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
"""
Module responsible for scheduler independent graph visualisation
"""
import os

from dask.core import get_deps


def _shorten_path(path):
    """Shorten paths for the visual graph"""
    if "/share/" in path:
        path = path[path.index("/share/") + 1 :]
    elif "/etc/" in path:
        path = path[path.index("/etc/") + 1 :]
    return path


def _as_html(msg):
    """Quick nasty convert text to html, avoid beautiful soup dep."""
    return str(msg).replace(">", "&gt;").replace("<", "&lt;")


class _HTMLTable:
    TABLE_TEMPLATE = """<table>
<tr>
{table_header}
</tr>
{table_cont}
</table>
"""

    def __init__(self, column_names):
        self._table_cont = ""
        self._table_header = "\n".join(
            [f"<th>{column_name}</th>" for column_name in column_names]
        )
        self._ncols = len(column_names)

    def add_row(self, *args):
        self._table_cont += (
            "\n<tr>" + "".join([f"<td>{_as_html(arg)}</td>" for arg in args]) + "</tr>"
        )

    def __str__(self):
        return self.TABLE_TEMPLATE.format(
            table_header=self._table_header, table_cont=self._table_cont
        )


class MermaidGraph:
    MERMAID_TEMPLATE = "graph TD\n{cont}"
    CARRIAGE_RETURN = "<br>"

    def __init__(self):
        self._cont = ""

    def add_node(self, nodeid, label=None, tooltip=None, url=None):
        if label:
            label = label.replace("\n", self.CARRIAGE_RETURN)
        self._cont += f'\n{nodeid}(["{label}"])'
        if tooltip:
            # https://mermaid-js.github.io/mermaid/#/flowchart?id=interaction
            tooltip = tooltip.replace("\n", self.CARRIAGE_RETURN)
            self._cont += f'\nclick {nodeid} callback "{tooltip}"'
        if url:
            self._cont += f'\nclick {nodeid} "{url}"'

    def add_connection(self, id1, id2):
        self._cont += f"\n{id1} --> {id2}"

    def __str__(self):
        return self.MERMAID_TEMPLATE.format(cont=self._cont)


class MermaidHTML:
    GRAPH_ENGINE = MermaidGraph
    HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<body>

<style>
div.mermaidTooltip {{
    position: absolute;
    text-align: left;
    max-width: 700px;
    padding: 2px;
    font-family: "trebuchet ms", verdana, arial, sans-serif;
    font-size: 12px;
    background: hsl(80, 100%, 96.2745098039%);
    border: 1px solid #aaaa33;
    border-radius: 2px;
    pointer-events: none;
    z-index: 100;
}}

tr:nth-child(even) {{ background: #CCC }}
tr:nth-child(odd) {{ background: #FFF }}
</style>

<div class="mermaid">
{graph}
</div>

<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@9/dist/mermaid.esm.min.mjs';
  mermaid.initialize({{
        startOnLoad: true,
        flowchart: {{ useMaxWidth: false, htmlLabels: true, curve: 'basis' }},
        securityLevel:'loose',
        maxTextSize: 99999999  // beyond this "Maximum text size in diagram exceeded"
  }});
</script>

{table}

</body>
</html>
"""

    def __init__(self, graph):
        self._graph, self._html_table = self._graph_engine_gen_with_table(graph)

    @classmethod
    def _get_tooltip(cls, tgt, args):
        args = " ".join(tuple(map(_shorten_path, args)))
        tgt = _shorten_path(tgt)
        return f"target:\n{tgt}\n\nargs:\n{args}"

    @classmethod
    def _get_url(cls, command, args):
        """Derive URL from the provided command and arguments"""
        url = None
        if args[0] == "improver":
            url = (
                "https://improver.readthedocs.io/en/latest/"
                f"improver.cli.{command.replace('-', '_')}.html"
            )
        return url

    @classmethod
    def _graph_engine_gen_with_table(cls, graph):
        table = _HTMLTable(["node ID", "command", "target", "args"])
        graph_engine = cls.GRAPH_ENGINE()
        node_target_id_map = {}
        node_id = 0
        pred_deps, _ = get_deps(graph)
        get_command = (
            lambda tgt: (graph[tgt][3], graph[tgt][2:])
            if graph[tgt][2] == "improver"
            else (graph[tgt][2], graph[tgt][2:])
        )
        for target in pred_deps:
            if target not in node_target_id_map:
                node_target_id_map[target] = node_id
                command, args = get_command(target)
                url = cls._get_url(command, args)
                graph_engine.add_node(
                    node_id,
                    label=f"{node_id}\n{command}",
                    tooltip=cls._get_tooltip(target, args),
                    url=url,
                )
                table.add_row(node_id, command, target, " ".join(args))
                node_id += 1

            for pred in pred_deps[target]:
                if pred not in node_target_id_map:
                    node_target_id_map[pred] = node_id
                    command, args = get_command(target)
                    url = cls._get_url(command, args)
                    graph_engine.add_node(
                        node_id,
                        label=f"{node_id}\n{command}",
                        tooltip=cls._get_tooltip(pred, args),
                        url=url,
                    )
                    table.add_row(node_id, command, pred, " ".join(args))
                    node_id += 1
                graph_engine.add_connection(
                    node_target_id_map[pred], node_target_id_map[target]
                )
        return graph_engine, table

    def __str__(self):
        return self.HTML_TEMPLATE.format(
            graph=str(self._graph), table=str(self._html_table)
        )

    def save(self, output_filepath):
        assert os.path.splitext(output_filepath)[-1] in [
            ".html",
        ], "Expecting graph output file extension to be .html"
        with open(output_filepath, "w") as fh:
            fh.write(str(self))


def visualise_graph(graph, output_filepath):
    """
    Args:
        graph (dict):
            Graph with keys representing 'targets' and values representing
            (function, *args).
        output_filepath (str):
            Node graph visualisation html output filepath.

    Returns:
        None:
    """
    MermaidHTML(graph).save(output_filepath)
