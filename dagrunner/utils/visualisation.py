# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
"""
Module responsible for scheduler independent graph visualisation
"""

import os


def _as_html(msg):
    """Quick nasty convert text to html, avoid beautiful soup dep."""
    return str(msg).replace(">", "&gt;").replace("<", "&lt;")


class HTMLTable:
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
            tooltip = tooltip.replace("\n", self.CARRIAGE_RETURN).replace('"', "")
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

.scrollable {{
    overflow-y: auto;
    overflow-x: auto;
}}

#mermaid1 {{
    height: 70vh;
}}

#table1 {{
    height: 30vh;
}}

</style>

<div id="mermaid1" class="mermaid scrollable">
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

<div id="table1" class="scrollable">
{table}
</div>

</body>
</html>
"""

    def __init__(self, mermaid, table=None):
        self._graph, self._html_table = mermaid, table

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
