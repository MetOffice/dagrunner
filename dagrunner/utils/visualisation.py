# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
"""
Module responsible for scheduler independent graph visualisation
"""

import base64
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

html, body {{
    margin: 0;
    padding: 0;
    height: 100%;
    overflow: hidden; /* Prevent page scrollbars */
    display: flex;
    flex-direction: column;
}}

td {{
    white-space: nowrap;
}}

#mermaid-container {{
    height: 70vh;
    min-height: 50px; /* Allow resizing very small */
    max-height: 90vh; /* Allow resizing very small */
    overflow: hidden; /* Add vertical scrollbar if needed */
    resize: vertical; /* Allow resizing */
    flex-shrink: 0; /* Prevent flex behaviour from overriding resize */
    border: 1px solid #ccc;
    position: relative; /* For positioning zoom buttons */
}}

.table_box {{
    min-height: 0;
    flex-grow: 1;
    position: relative;
}}

.table_content {{
    overflow: auto;
    width: 100%;
    height: 100%;
}}

.wrap-toggle {{
    position: absolute;
    bottom: 1rem;
    right: 1rem;
    cursor: pointer;
}}

#diagram-wrapper {{
    cursor: grab;
}}

#diagram-wrapper:active {{
    cursor: grabbing;
}}

.mermaid {{
transform-origin: 0 0; /* Set the origin for scaling */
}}

#zoom-controls {{
    position: absolute;
    right: 10px;
    bottom: 10px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 5px;
}}

button {{
    padding: 5px;
    font-size: 14px;
    min-width: 25px;
}}

#save-diagram {{
    position: absolute;
    top: 10px;
    right: 10px;
    cursor: pointer;
}}

#banner {{
    position: absolute;
    bottom: 2px;
    left: 2px;
    padding: 0px;
    font-size: 16px;
    cursor: pointer;
}}

</style>

<div id="mermaid-container">
    <button id="save-diagram" style="margin-left: auto;">📥</button> <!-- Button aligned to the right -->
    <div id="diagram-wrapper">
        <div class="mermaid">
{graph}
        </div>
    </div>

    <div id="banner">
        <a href="https://github.com/MetOffice/dagrunner" target="_blank">
        <img src="https://raw.githubusercontent.com/MetOffice/dagrunner/refs/heads/main/docs/symbol.svg"/>
        <text>DAGrunner visualisation</text>
        </a>
    </div>

    <div id="zoom-controls">
        <button id="zoom-in" title="zoom-in">+</button>
        <div>
            <button id="toggle-zoom" title="make zoom cursor-relative or origin-relative">🖱️</button>
            <button id="zoom-reset" title="reset zoom and offset">🏠</button>
        </div>
        <button id="zoom-out" title="zoom-out">-</button>
    </div>
</div>

<script type="module">
import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11.0/dist/mermaid.esm.min.mjs';
mermaid.initialize({{
    startOnLoad: true,
    flowchart: {{ useMaxWidth: false, htmlLabels: true, curve: 'basis' }},
    securityLevel:'loose',
    maxTextSize: 99999999  // beyond this "Maximum text size in diagram exceeded"
}});

const wrapper = document.getElementById('diagram-wrapper');
const mermaidDiagram = document.querySelector('.mermaid');
const toggleButton = document.getElementById('toggle-zoom');
const saveButton = document.getElementById('save-diagram');
const zoomInButton = document.getElementById('zoom-in');
const zoomOutButton = document.getElementById('zoom-out');
const zoomResetButton = document.getElementById('zoom-reset');
const wrapToggleButton = document.querySelector('.wrap-toggle');

let scale = 1;
let offsetX = 0;
let offsetY = 0;
let zoomRelativeToCursor = true; // Default behaviour: cursor-relative zoom
let isWrapped = false;  // Tracks whether text is wrapped or not

const updateTransform = () => {{
    mermaidDiagram.style.transform = `translate(${{offsetX}}px, ${{offsetY}}px) scale(${{scale}})`;
}};

toggleButton.addEventListener('click', () => {{
    zoomRelativeToCursor = !zoomRelativeToCursor;
    toggleButton.textContent = `${{zoomRelativeToCursor ? '🖱️' : '🧭'}}`;
}});

saveButton.addEventListener('click', () => {{
    // Extract the rendered SVG from the DOM
    const svgElement = document.querySelector('#mermaid-container svg');
    if (!svgElement) {{
        alert('No diagram found to save!');
        return;
    }}

    // Serialize the SVG to a string
    const serializer = new XMLSerializer();
    const svgContent = serializer.serializeToString(svgElement);

    // Create a Blob from the SVG string
    const blob = new Blob([svgContent], {{ type: 'image/svg+xml;charset=utf-8' }});

    // Create a link element to trigger the download
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'mermaid-diagram.svg';
    link.click();

    // Clean up the temporary object URL
    URL.revokeObjectURL(link.href);
}});

// Zoom functionality
    zoomInButton.addEventListener('click', () => {{
    const zoomStep = 0.1;
    const newScale = Math.min(scale + zoomStep, 2); // Limit zoom-in
    scale = newScale;
    updateTransform();
}});

zoomOutButton.addEventListener('click', () => {{
    const zoomStep = 0.1;
    const newScale = Math.max(scale - zoomStep, 0.2); // Limit zoom-out
    scale = newScale;
    updateTransform();
}});

// Reset Zoom functionality
zoomResetButton.addEventListener('click', () => {{
    // Reset zoom scale and position
    scale = 1;
    offsetX = 0;
    offsetY = 0;
    updateTransform();
}});

// Zoom functionality with mouse wheel
wrapper.addEventListener('wheel', (event) => {{
    event.preventDefault();
    const zoomStep = 0.1;
    const minScale = 0.2;
    const maxScale = 2;
    const newScale = Math.min(Math.max(scale + (event.deltaY > 0 ? -zoomStep : zoomStep), minScale), maxScale);
    if (zoomRelativeToCursor) {{
        // Cursor-relative zoom
        const rect = wrapper.getBoundingClientRect();
        const cursorX = event.clientX - rect.left; // Cursor position relative to wrapper
        const cursorY = event.clientY - rect.top;
        offsetX -= (cursorX - offsetX) * (newScale / scale - 1);
        offsetY -= (cursorY - offsetY) * (newScale / scale - 1);
    }}
    scale = newScale;
    updateTransform();
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
        const deltaX = event.clientX - startX;
        const deltaY = event.clientY - startY;
        offsetX += deltaX;
        offsetY += deltaY;
        startX = event.clientX;
        startY = event.clientY;
        updateTransform();
    }}
}});

wrapper.addEventListener('mouseup', () => {{
    isDragging = false;
}});

wrapper.addEventListener('mouseleave', () => {{
    isDragging = false;
}});

// Text wrap toggle functionality
wrapToggleButton.addEventListener('click', () => {{
    const tds = document.querySelectorAll('.table_content td');
    isWrapped = !isWrapped;  // Toggle wrap state
    tds.forEach(td => {{
        td.style.whiteSpace = isWrapped ? 'normal' : 'nowrap';  // Apply the appropriate wrap style
    }});
    wrapToggleButton.textContent = isWrapped ? '🔄' : '➡️';  // Change the button symbol
}});

</script>

<div class="table_box">
    <div class="table_content">
{table}
        <button class="wrap-toggle">➡️</button>
    </div>
</div>

</body>
</html>
"""  # noqa: E501

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
