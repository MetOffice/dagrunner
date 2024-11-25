# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
"""
Module responsible for scheduler independent graph visualisation
"""
import base64
import os
import requests


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
    MERMAID_TEMPLATE = "---\ntitle: {title}\n---\ngraph TD\n{cont}"
    CARRIAGE_RETURN = "<br>"

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
        from IPython.display import Image, Markdown, display
        import notebook

        # Mermaid graph definition
        graph = self.__str__()

        notebook_version = tuple(map(int, notebook.__version__.split('.')))
        if notebook_version >= (7, 1):
            # Use native Mermaid rendering in Markdown
            display(Markdown(graph))
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

#table1 {{
    height: 30vh;
}}

#mermaid-container {{
    width: 100%;
    height: 70vh;
    overflow: hidden;
    border: 1px solid #ccc;
    position: relative;
}}
#diagram-wrapper {{
    width: 100%;
    height: 100%;
    cursor: grab;
}}
#diagram-wrapper:active {{
    cursor: grabbing;
}}
.mermaid {{
    transform-origin: 0 0; /* Set the origin for scaling */
}}

</style>

<div id="mermaid-container">
<div id="diagram-wrapper">
<div class="mermaid">
{graph}
</div>
</div>
</div>

<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@9/dist/mermaid.esm.min.mjs';
  mermaid.initialize({{
        startOnLoad: true,
        flowchart: {{ useMaxWidth: false, htmlLabels: true, curve: 'basis' }},
        securityLevel:'loose',
        maxTextSize: 99999999  // beyond this "Maximum text size in diagram exceeded"
  }});

  // Zoom and pan functionality
  const wrapper = document.getElementById('diagram-wrapper');
  const mermaidDiagram = document.querySelector('.mermaid');
  let scale = 1;
  let originX = 0;
  let originY = 0;

  // Zoom functionality
  wrapper.addEventListener('wheel', (event) => {{
    event.preventDefault();
    const zoomStep = 0.1;
    const minScale = 0.5;
    const maxScale = 4;
    scale += event.deltaY > 0 ? -zoomStep : zoomStep;
    scale = Math.min(Math.max(scale, minScale), maxScale);
    mermaidDiagram.style.transform = `scale(${{scale}}) translate(${{originX}}px, ${{originY}}px)`;
  }});

  // Pan functionality
  let isDragging = false;
  let startX, startY;
  wrapper.addEventListener('mousedown', (event) => {{
    isDragging = true;
    startX = event.clientX;
    startY = event.clientY;
  }});

  wrapper.addEventListener('mousemove', (event) => {{
    if (isDragging) {{
      const deltaX = (event.clientX - startX) / scale;
      const deltaY = (event.clientY - startY) / scale;
      originX += deltaX;
      originY += deltaY;
      startX = event.clientX;
      startY = event.clientY;
      mermaidDiagram.style.transform = `scale(${{scale}}) translate(${{originX}}px, ${{originY}}px)`;
    }}
  }});

  wrapper.addEventListener('mouseup', () => {{
    isDragging = false;
  }});

  wrapper.addEventListener('mouseleave', () => {{
    isDragging = false;
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
