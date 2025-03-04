class TableStandardFmt extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
        this.offsetX = 0;
        this.offsetY = 0;
        this.scale = 1;
        this.zoomRelativeToCursor = true;
        this.isDragging = false;
        this.isWrapped = false;
        this.user_initialised_mermaid = true;
    }

    connectedCallback() {
        this.render();
        this.setupRowClickHandling();
        this.setupMermaid();
        this.setupPanning();
        this.setupZooming();
        this.setupSvgExport();
        this.setupTextWrapToggle();
        this.setupMermaidClickHandling();
        this.setupThemeToggle();
    }

    render() {
        this.shadowRoot.innerHTML = `
            <style>
                :host {
                    display: flex;
                    flex-direction: column;
                    height: 100%;

                    color-scheme: light dark;
                    --primary-color: light-dark(rgb(43, 43, 43),rgb(233, 233, 233));
                    --primary-background: light-dark(rgb(255, 255, 255),rgb(43, 43, 43));
                    --highlight-color: light-dark(yellow,rgb(173, 114, 54));
                    --primary-accent: light-dark(rgb(190, 190, 190),rgb(100, 100, 100));

                    color: var(--primary-color);
                    background-color: var(--primary-background);
                    transition: color 0.4s, background-color 0.4s;
                }

                /* Force light or dark mode based on data-theme */
                :host([data-theme="light"]) {
                    color-scheme: light;
                }

                :host([data-theme="dark"]) {
                    color-scheme: dark;
                }

                #mermaid-container {
                    height: 70vh;
                    min-height: 50px; /* Allow resizing very small */
                    max-height: 90vh; /* Allow resizing very small */
                    overflow: hidden; /* Add vertical scrollbar if needed */
                    resize: vertical; /* Allow resizing */
                    flex-shrink: 0; /* Prevent flex behaviour from overriding resize */
                    position: relative; /* For positioning zoom buttons */
                    border: 1px solid var(--primary-accent);
                    border-radius: 5px;
                    box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
                }

                .table_box {
                    min-height: 0;
                    flex-grow: 1;
                    position: relative;
                }

                .table_content {
                    overflow: auto;
                    width: 100%;
                    height: 100%;
                }

                .wrap-toggle {
                    position: absolute;
                    bottom: 1rem;
                    right: 1rem;
                    cursor: pointer;
                }

                #diagram-wrapper {
                    cursor: grab;
                }

                #diagram-wrapper:active {
                    cursor: grabbing;
                }

                #zoom-controls {
                    position: absolute;
                    right: 10px;
                    bottom: 10px;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    gap: 5px;
                }

                button {
                    padding: 5px;
                    font-size: 14px;
                    min-width: 25px;
                    cursor: pointer;
                }

                #save-diagram {
                    position: absolute;
                    top: 10px;
                    right: 10px;
                }

                #toggle-theme {
                    background-color: transparent;
                    color: transparent;
                    border-color: transparent;
                }

                #banner {
                    position: absolute;
                    bottom: 2px;
                    left: 2px;
                    padding: 0px;
                    font-size: 16px;
                    cursor: pointer;
                }

            </style>

            <div id="mermaid-container">
                <button id="toggle-theme" type="button">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16">
                    <circle r="7" cx="8" cy="8" stroke=var(--primary-color) fill="none" />
                    <path stroke=var(--primary-color) fill=var(--primary-color) d="M8 15A1 1 0 0 0 8 1" />
                </svg>
                </button>
                <button id="save-diagram">📥</button>
                <div id="diagram-wrapper">
                    <slot name="mermaid"></slot>
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

            <div class="table_box">
                <div class="table_content">
                    <slot name="table"></slot>
                    <button class="wrap-toggle" title="word wrap toggle">➡️</button>
                </div>
            </div>
        `;
    }

    setupThemeToggle() {
        const themeToggleButton = this.shadowRoot.querySelector("#toggle-theme");
        let theme = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
        this.setAttribute("data-theme", theme);
    
        const updateTheme = () => {
            theme = theme === "light" ? "dark" : "light";
            this.setAttribute("data-theme", theme);
    
            // Only update Mermaid theme if we were the ones who initialized it
            const mermaidDiv = this.querySelector('.mermaid');
            const alreadyInitialized = mermaidDiv?.querySelector("svg") !== null;
            this.initializeMermaidWithTheme(theme);
        };
    
        themeToggleButton.addEventListener("click", updateTheme);
    }

    setupRowClickHandling() {
        const slot = this.shadowRoot.querySelector('slot[name="table"]');
        slot.addEventListener('slotchange', () => {
            const table = this.querySelector('table');
            if (table) {
                table.querySelectorAll('tr').forEach(row => {
                    row.addEventListener('click', () => {
                        this.highlightRow(row.id);
                    });
                });
            }
        });
    }

    setupMermaid() {
        const slot = this.shadowRoot.querySelector('slot[name="mermaid"]');
        slot.addEventListener('slotchange', async () => {
            const mermaidDiv = this.querySelector('.mermaid');
            if (!mermaidDiv) return;
    
            const alreadyInitialized = mermaidDiv.querySelector("svg") !== null;
    
            if (!alreadyInitialized) {
                this.user_initialised_mermaid = false;

                // If Mermaid.js isn't loaded, load it first
                if (typeof window.mermaid === "undefined") {
                    await this.loadMermaidScript();
                }
    
                // Now, initialize it with the correct theme
                const theme = this.getAttribute("data-theme") || "light";
                this.initializeMermaidWithTheme(theme);
            }
            mermaid.init(undefined, mermaidDiv);
            this.mermaidDiagram = mermaidDiv;
        });
    }

    async loadMermaidScript() {
        return new Promise((resolve, reject) => {
            if (typeof window.mermaid !== "undefined") {
                resolve();
                return;
            }
    
            const script = document.createElement("script");
            script.src = "https://cdn.jsdelivr.net/npm/mermaid@9/dist/mermaid.min.js";
            script.onload = () => {
                console.log("Mermaid.js loaded dynamically");
                resolve();
            };
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    initializeMermaidWithTheme(theme) {
        const mermaidDiv = this.querySelector('.mermaid');
        if (!mermaidDiv || typeof window.mermaid === "undefined") return;
        const alreadyInitialized = mermaidDiv.querySelector("svg") !== null;

        if (!alreadyInitialized) {
            console.log("Mermaid initialised dynamically");
            mermaid.initialize({
                theme: theme === "dark" ? "dark" : "default",
                startOnLoad: false,
                flowchart: { useMaxWidth: false, htmlLabels: true, curve: 'basis' },
                securityLevel:'loose',  // required for mermaid@9 tooltip functionality
                maxTextSize: 99999999  // beyond this "Maximum text size in diagram exceeded"
            });
        } else {
            alert("mermaid re-initialisation for dynamic theme change not yet supported");
        }
    }

    setupMermaidClickHandling() {
        const container = this.shadowRoot.querySelector("#diagram-wrapper");
    
        container.addEventListener("click", (event) => {
            const node = event.target.closest(".node"); // Find the nearest .node element
            if (!node) return;
    
            const match = node.textContent.match(/^\d+/); // Extract the leading number (row ID)
            if (match) {
                const rowID = "row" + match[0]; // Assuming row IDs are formatted as 'row<number>'
                this.highlightRow(rowID);
            }
        });
    }

    highlightRow(rowID) {
        const row = this.querySelector(`#${rowID}`);
        if (row) {
            if (this.lastHighlightedRow) {
                this.lastHighlightedRow.classList.remove('highlighted');
            }
            row.classList.add('highlighted');
            row.scrollIntoView({ behavior: 'smooth', block: 'center' });
            this.lastHighlightedRow = row;
        }
    }

    setupPanning() {
        const wrapper = this.shadowRoot.querySelector('#diagram-wrapper');

        const updateTransform = () => {
            if (this.mermaidDiagram) {
                this.mermaidDiagram.style.transform = `translate(${this.offsetX}px, ${this.offsetY}px) scale(${this.scale})`;
            }
        };

        let startX, startY;

        wrapper.addEventListener('mousedown', (event) => {
            this.isDragging = true;
            startX = event.clientX;
            startY = event.clientY;
        });

        wrapper.addEventListener('mousemove', (event) => {
            if (this.isDragging) {
                const deltaX = event.clientX - startX;
                const deltaY = event.clientY - startY;
                this.offsetX += deltaX;
                this.offsetY += deltaY;
                startX = event.clientX;
                startY = event.clientY;
                updateTransform();
            }
        });

        wrapper.addEventListener('mouseup', () => { this.isDragging = false; });
        wrapper.addEventListener('mouseleave', () => { this.isDragging = false; });
    }

    setupZooming() {
        const wrapper = this.shadowRoot.querySelector('#diagram-wrapper');
        const zoomInButton = this.shadowRoot.querySelector('#zoom-in');
        const zoomOutButton = this.shadowRoot.querySelector('#zoom-out');
        const zoomResetButton = this.shadowRoot.querySelector('#zoom-reset');
        const toggleButton = this.shadowRoot.querySelector('#toggle-zoom');

        const updateTransform = () => {
            if (this.mermaidDiagram) {
                this.mermaidDiagram.style.transform = `translate(${this.offsetX}px, ${this.offsetY}px) scale(${this.scale})`;
            }
        };

        wrapper.addEventListener('wheel', (event) => {
            event.preventDefault();
            const zoomStep = 0.1;
            const minScale = 0.2;
            const maxScale = 2;
            const newScale = Math.min(Math.max(this.scale + (event.deltaY > 0 ? -zoomStep : zoomStep), minScale), maxScale);

            if (this.zoomRelativeToCursor) {
                const rect = wrapper.getBoundingClientRect();
                const cursorX = event.clientX - rect.left;
                const cursorY = event.clientY - rect.top;
                this.offsetX -= (cursorX - this.offsetX) * (newScale / this.scale - 1);
                this.offsetY -= (cursorY - this.offsetY) * (newScale / this.scale - 1);
            }

            this.scale = newScale;
            updateTransform();
        });

        zoomInButton.addEventListener('click', () => {
            this.scale = Math.min(this.scale + 0.1, 2);
            updateTransform();
        });

        zoomOutButton.addEventListener('click', () => {
            this.scale = Math.max(this.scale - 0.1, 0.2);
            updateTransform();
        });

        zoomResetButton.addEventListener('click', () => {
            this.scale = 1;
            this.offsetX = 0;
            this.offsetY = 0;
            updateTransform();
        });

        toggleButton.addEventListener('click', () => {
            this.zoomRelativeToCursor = !this.zoomRelativeToCursor;
            toggleButton.textContent = this.zoomRelativeToCursor ? '🖱️' : '🧭';
        });
    }

    setupSvgExport() {
        const saveButton = this.shadowRoot.querySelector('#save-diagram');

        saveButton.addEventListener('click', () => {
            const svgElement = this.querySelector('.mermaid svg');
            if (!svgElement) {
                alert('No diagram found to save!');
                return;
            }

            const serializer = new XMLSerializer();
            const svgContent = serializer.serializeToString(svgElement);
            const blob = new Blob([svgContent], { type: 'image/svg+xml;charset=utf-8' });

            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = 'mermaid-diagram.svg';
            link.click();

            URL.revokeObjectURL(link.href);
        });
    }

    setupTextWrapToggle() {
        const wrapToggleButton = this.shadowRoot.querySelector('.wrap-toggle');

        wrapToggleButton.addEventListener('click', () => {
            const tds = this.querySelectorAll('td');
            this.isWrapped = !this.isWrapped;
            tds.forEach(td => td.style.whiteSpace = this.isWrapped ? 'normal' : 'nowrap');
            wrapToggleButton.textContent = this.isWrapped ? '🔄' : '➡️';
        });
    }
}

// Apply styles globally to ensure they affect the light DOM elements
const style = document.createElement('style');
style.textContent = `
    html, body {
        margin: 0;
        padding: 0;
        height: 100%;
        overflow: hidden; /* Prevent page scrollbars */
        display: flex;
        flex-direction: column;
    }

    div.mermaidTooltip {
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
    }

    .mermaid {
        transform-origin: 0 0; /* Set the origin for scaling */
    }

    .highlighted {
        background: var(--highlight-color) !important;
    }

    tr:nth-child(even) { background: var(--primary-background) }
    tr:nth-child(odd) { background: var(--primary-accent) }

    td {
        white-space: nowrap;
    }
    th, td {
        text-align: left;
        vertical-align: top; /* Top align */
    }

    table thead th { background: var(--primary-background); position: sticky; top: 0; z-index: 1; }

`;
document.head.appendChild(style);

customElements.define('mermaid-table-standard', TableStandardFmt);
