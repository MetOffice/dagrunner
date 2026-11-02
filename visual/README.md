# Visualisation

## Generating Workflow Plots

[create_plots.py](create_plots.py) generates linked HTML visualisations from a
NetworkX graph: a collapsed overview, detail pages for each value of a chosen node
attribute, and an index page for selecting configurations. Installing DAGrunner
installs this utility as the `dagrunner-plot` command.
The plotting script and browser assets are deployed as shared data, not as a
separate importable `visual` package; `dagrunner` remains the only top-level package.

Pass the importable dotted path to your graph or graph-building function, plus a
JSON file defining how the two plot levels should be displayed:

```sh
dagrunner-plot my_workflow.build_graph \
		--networkx-graph-kwargs suite_name example \
		--plot-config-filepath plots.json --output-root graphs
```

Replace `my_workflow.build_graph` with your own importable graph factory. Repeat
`--networkx-graph-kwargs key value` for additional keyword arguments; CLI values
are strings. A factory can return a graph or a `(graph, metadata)` tuple.
For nodes with `chain`, `leadtime`, `system`, and `step` attributes, `plots.json`
could contain:

```json
{
	"index_title": "Workflow visualisation",
	"detail_by": "chain",
	"level1": {
		"collapse_properties": ["leadtime", "system", "step"],
		"label_by": ["chain"]
	},
	"level2": {
		"collapse_properties": ["leadtime"],
		"label_by": ["system", "step"],
		"group_by": ["chain"]
	}
}
```

Choose attribute names to match your graph's nodes. Open the generated
`graphs/index.html` in a browser. Use `--override-existing` to replace existing
plots, `--webcomponent /path/to/mermaid-table-standard.js` to bundle a local
component instead of the default CDN version, and `dagrunner-plot --help` for
all options.

## Web Component

[mermaid-table-standard.js](mermaid-table-standard.js) provides a
`<mermaid-table-standard>` web component combining a Mermaid diagram with a lookup
table. Load it as a classic script with `defer`; Mermaid 9 is downloaded from
jsDelivr automatically unless already loaded.

## Minimal Example

Save the following HTML alongside the JavaScript file and open it in a browser:

```html
<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<title>Workflow</title>
	<script src="mermaid-table-standard.js" defer></script>
</head>
<body>
	<mermaid-table-standard>
		<pre class="mermaid" slot="mermaid">
graph LR
	0["0: Input"] --> 1["1: Output"]
	click 0 callback "Show input"
	click 1 callback "Show output"
		</pre>
		<table slot="table">
			<thead><tr><th>id</th><th>description</th></tr></thead>
			<tbody>
				<tr id="row0"><td>0</td><td>Input</td></tr>
				<tr id="row1"><td>1</td><td>Output</td></tr>
			</tbody>
		</table>
	</mermaid-table-standard>
</body>
</html>
```

Use matching numeric node IDs and `row<ID>` table row IDs to link the two views.
Only use trusted diagram and table content: Mermaid runs with `securityLevel: 'loose'`.
The component also applies page-level styles, including disabling page scrolling.

## Controls

- Drag the diagram to pan; use the mouse wheel or zoom buttons to zoom.
- Reset restores the original position and scale; the adjacent button switches
  between cursor-relative and origin-relative wheel zoom.
- Click a diagram node to highlight its row; click a table row to centre its node.
- Drag the diagram's bottom-right resize handle to change its height.
- Click table headings to sort; use the table buttons to toggle wrapping and line breaks.
- Download exports the diagram as SVG. The theme button switches light/dark mode
  and remembers the selection where browser storage is available.

## Embedding And Extensions

In an iframe, the component announces `{ type: 'dagrunner:theme-ready' }` to its
parent. A parent can reply to the iframe with
`{ type: 'dagrunner:set-theme', theme: 'light' }` (or `'dark'`) using `postMessage`.
Once a valid parent theme message arrives, the embedded theme button is hidden.
Standalone pages keep their own button. Parents should validate message source
and origin and resend their theme after iframe navigation.

For custom navigation, use `component.upsertTopLeftLink(...)` and
`bindSubgraphClicks(...)`. The developer header in
[mermaid-table-standard.js](mermaid-table-standard.js) documents these helpers,
the `mermaidRendered` event, and integration constraints.

