class TableStandardFmt extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
        this.offsetX = 0;
        this.offsetY = 0;
        this.scale = 1;
        this.zoomRelativeToCursor = true;
        this.isDragging = false;
        this.activePointerId = null;
        this.isWrapped = false;
        this.user_initialised_mermaid = true;
        this.table_ascending = true;
        this.br_hidden = false;
        this.lastClickedMermaidNode = null;

        this.svg_theme_toggle = `
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24">
                <circle r="10" cx="12" cy="12" stroke-width="2" stroke=var(--primary-color) fill="none" />
                <path stroke-width="0" fill=var(--primary-color) d="M12 22A1 1 0 0 0 12 2" />
            </svg>
            `;

        this.svg_download = `
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-download-icon lucide-download"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>
        `;

        this.svg_reset = `
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-house-icon lucide-house"><path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"/><path d="M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>
        `;

        this.svg_zoomin = `
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-zoom-in-icon lucide-zoom-in"><circle cx="11" cy="11" r="8"/><line x1="21" x2="16.65" y1="21" y2="16.65"/><line x1="11" x2="11" y1="8" y2="14"/><line x1="8" x2="14" y1="11" y2="11"/></svg>
        `;

        this.svg_zoomout = `
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-zoom-out-icon lucide-zoom-out"><circle cx="11" cy="11" r="8"/><line x1="21" x2="16.65" y1="21" y2="16.65"/><line x1="8" x2="14" y1="11" y2="11"/></svg>
        `;

        this.svg_zoom_mouse_rel = `
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-mouse-icon lucide-mouse"><rect x="5" y="2" width="14" height="20" rx="7"/><path d="M12 6v4"/></svg>
        `;

        this.svg_zoom_orig_rel = `
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-compass-icon lucide-compass"><path d="m16.24 7.76-1.804 5.411a2 2 0 0 1-1.265 1.265L7.76 16.24l1.804-5.411a2 2 0 0 1 1.265-1.265z"/><circle cx="12" cy="12" r="10"/></svg>
        `;

        this.svg_table_text_wrap = `
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-wrap-text-icon lucide-wrap-text"><line x1="3" x2="21" y1="6" y2="6"/><path d="M3 12h15a3 3 0 1 1 0 6h-4"/><polyline points="16 16 14 18 16 20"/><line x1="3" x2="10" y1="18" y2="18"/></svg>
        `;

        this.svg_table_text_nowrap = `
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-align-justify-icon lucide-align-justify"><path d="M3 12h18"/><path d="M3 18h18"/><path d="M3 6h18"/></svg>
        `;

        this.svg_delim_br = `
            <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <g transform="translate(0, -5) scale(1, 1.5)">
            <text x="12" y="12" font-size="12"  font-family="Arial" fill="currentColor"
                    text-anchor="middle" dominant-baseline="central">
                &lt;br&gt;
            </text>
            </g>
            </svg>`;

        this.svg_delim_semicol = `
            <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <g transform="translate(0, -5) scale(1, 1.5)">
            <text x="12" y="12" font-size="12"  font-family="Arial" fill="currentColor"
                    text-anchor="middle" dominant-baseline="central">
                ;
            </text>
            </g>
            </svg>`;
    }

    connectedCallback() {
        this.render();
        this.registerMermaidClickCallback();
        this.setupRowClickHandling();
        this.setupMermaid();
        this.setupPanning();
        this.setupZooming();
        this.setupSvgExport();
        this.setupTextWrapToggle();
        this.setupMermaidClickHandling();
        this.setupThemeToggle();
        this.setupTableHeaderClickHandling();
        this.setupTextNewlineDelimToggle();
    }

    registerMermaidClickCallback() {
        // Mermaid `click <id> callback` expects a global function named `callback`.
        // Provide a default implementation if one does not already exist.
        if (typeof window.callback !== 'function') {
            window.callback = (nodeId) => {
                document.querySelectorAll('mermaid-table-standard').forEach(component => {
                    if (typeof component.handleMermaidNodeCallback === 'function') {
                        component.handleMermaidNodeCallback(nodeId);
                    }
                });
            };
        }
    }

    handleMermaidNodeCallback(nodeId) {
        if (nodeId === null || nodeId === undefined) {
            return;
        }
        this.highlightRow(`row${String(nodeId)}`);
    }

    getTopLeftControlsContainer() {
        return this.shadowRoot ? this.shadowRoot.querySelector('#diag-top-left-controls') : null;
    }

    upsertTopLeftLink({ id, href, textContent, target } = {}) {
        if (!id) {
            throw new Error('upsertTopLeftLink requires a non-empty id');
        }

        const controls = this.getTopLeftControlsContainer();
        if (!controls) {
            return null;
        }

        let link = this.shadowRoot.getElementById(id);
        if (!link || link.tagName !== 'A') {
            link = document.createElement('a');
            link.id = id;
            controls.appendChild(link);
        }

        if (href !== undefined) {
            link.href = href;
        }
        if (textContent !== undefined) {
            link.textContent = textContent;
        }
        if (target !== undefined) {
            link.target = target;
        }

        return link;
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
                    --primary-accent: light-dark(rgb(190, 190, 190),rgb(85, 85, 85));

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

                #table-controls {
                    position: absolute;
                    bottom: 1rem;
                    right: 1rem;
                    cursor: pointer;
                    align-items: center;
                    z-index: 1;
                }

                #diagram-wrapper {
                    position: absolute;
                    inset: 0;
                    overflow: hidden;
                    z-index: 0;
                    cursor: grab;
                    user-select: none;
                    -webkit-user-select: none;
                    touch-action: none;
                }

                #diagram-wrapper:active {
                    cursor: grabbing;
                }

                #diagram-wrapper * {
                    cursor: grab;
                    user-select: none;
                    -webkit-user-select: none;
                }

                #diagram-wrapper ::slotted(*) {
                    cursor: grab;
                    user-select: none;
                    -webkit-user-select: none;
                    -webkit-user-drag: none;
                }

                #diagram-wrapper.dragging,
                #diagram-wrapper.dragging * {
                    cursor: grabbing !important;
                }

                #diagram-wrapper.dragging ::slotted(*) {
                    cursor: grabbing !important;
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

                #diag-top-left-controls {
                    position: absolute;
                    left: 0px;
                    top: 0px;
                    display: flex;
                    flex-direction: row;
                    align-items: center;
                    gap: 20px;
                    z-index: 1;
                }

                #diag-top-right-controls {
                    position: absolute;
                    right: 10px;
                    top: 10px;
                    display: flex;
                    flex-direction: row;
                    align-items: center;
                    gap: 5px;
                    z-index: 1;
                }

                button {
                    padding: 5px;
                    font-size: 14px;
                    min-width: 25px;
                    cursor: pointer;
                }

                #toggle-theme {
                    background-color: transparent;
                    color: transparent;
                    border-color: transparent;
                }

                a {
                    cursor: pointer;
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
                <dev id="diag-top-left-controls">
                    <button id="toggle-theme" title="theme-toggle" type="button">${this.svg_theme_toggle}</button>
                </dev>

                <dev id="diag-top-right-controls">
                    <button id="save-diagram" title="save svg">${this.svg_download}</button>
                </dev>

                <div id="diagram-wrapper">
                    <slot name="mermaid"></slot>
                </div>

                <div id="banner">
                    <a href="https://github.com/MetOffice/dagrunner" target="_blank">
                    <img src="https://raw.githubusercontent.com/MetOffice/dagrunner/refs/heads/main/docs/logo.svg"/>
                    <text>DAGrunner visualisation</text>
                    </a>
                </div>

                <div id="zoom-controls">
                    <button id="zoom-in" title="zoom-in">${this.svg_zoomin}</button>
                    <div>
                        <button id="toggle-zoom" title="make zoom cursor-relative or origin-relative">${this.svg_zoom_mouse_rel}</button>
                        <button id="zoom-reset" title="reset zoom and offset">${this.svg_reset}</button>
                    </div>
                    <button id="zoom-out" title="zoom-out">${this.svg_zoomout}</button>
                </div>
            </div>

            <div class="table_box">
                <div class="table_content">
                    <slot name="table"></slot>
                    <div id="table-controls">
                        <button class="newline_delim" title="newline delimiter toggle">${this.svg_delim_br}</button>
                        <button class="wrap-toggle" title="word wrap toggle">${this.svg_table_text_nowrap}</button>
                    </div>
                </div>
            </div>
        `;
    }

    setupTableHeaderClickHandling() {
        const slot = this.shadowRoot.querySelector('slot[name="table"]');
        slot.addEventListener('slotchange', () => {
            const table = this.querySelector('table');
            if (table) {
                table.querySelectorAll('th').forEach(th => {
                    th.addEventListener('click', () => {
                        this.sortTable(th.cellIndex);
                    });

                    // requires this web component to be used as a module
                    // const svg = document.createElement('img');
                    // svg.src = new URL('./resources/arrow-down-a-z.svg', import.meta.url);
                    // svg.alt = "sort";
                    // th.appendChild(svg);
                    th.innerText += ' [---]';
                });
            }
        }
        );
    }

    sortTable(columnIndex) {
        var rows, switching, i, x, y, shouldSwitch;
        const table = this.querySelector('table');

        var col_num = 0;
        var slice;
        table.querySelectorAll('th').forEach(th => {
            if (col_num === columnIndex){
                slice = this.table_ascending === true ? "[a-z]" : "[z-a]";
            } else {
                slice = '[---]';
            }
            th.innerText = th.innerText.slice(0, -5) + slice;
            col_num++;
        });

        switching = true;
        while (switching) {
            switching = false;
            rows = table.rows;
            for (i = 1; i < (rows.length - 1); i++) {
                shouldSwitch = false;
                x = rows[i].getElementsByTagName("TD")[columnIndex];
                y = rows[i + 1].getElementsByTagName("TD")[columnIndex];
                if (this.table_ascending) {
                    if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                        shouldSwitch = true;
                        break;
                    }
                } else {
                    if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
                        shouldSwitch = true;
                        break;
                    }
                }
            }
            if (shouldSwitch) {
                rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                switching = true;
            }
        }
        this.table_ascending = !this.table_ascending;
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
            const tbody = table.querySelector('tbody');
            if (tbody) {
                tbody.querySelectorAll('tr').forEach(row => {
                row.addEventListener('click', () => {
                    this.highlightRow(row.id);
                });
                });
            }
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
            mermaid.init(undefined, mermaidDiv).then(() => {
                this.dispatchEvent(new CustomEvent("mermaidRendered", { bubbles: true }));
            });
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
            console.warn("Mermaid re-initialization for dynamic theme change is not yet supported.");
        }
    }

    setupMermaidClickHandling() {
        const container = this.shadowRoot.querySelector("#diagram-wrapper");

        container.addEventListener("click", (event) => {
            const node = event.target.closest(".node"); // Find the nearest .node element
            if (!node) return;

            this.lastClickedMermaidNode = node;

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
        const controls = '#zoom-controls, #diag-top-left-controls, #diag-top-right-controls, #banner, #banner *';

        const updateTransform = () => {
            if (this.mermaidDiagram) {
                this.mermaidDiagram.style.transform = `translate(${this.offsetX}px, ${this.offsetY}px) scale(${this.scale})`;
            }
        };

        let startX = 0;
        let startY = 0;

        const stopDragging = (event) => {
            if (event && event.pointerId !== undefined && this.activePointerId !== null && event.pointerId !== this.activePointerId) {
                return;
            }
            this.isDragging = false;
            this.activePointerId = null;
            this.classList.remove('dragging');
            wrapper.classList.remove('dragging');
            if (this.mermaidDiagram) {
                this.mermaidDiagram.classList.remove('dragging');
            }
            document.body.style.cursor = '';
        };

        const startDragging = (event, pointerId = null) => {
            if (event.target && event.target.closest && event.target.closest(controls)) {
                return;
            }

            this.isDragging = true;
            this.activePointerId = pointerId;
            startX = event.clientX;
            startY = event.clientY;
            this.classList.add('dragging');
            wrapper.classList.add('dragging');
            if (this.mermaidDiagram) {
                this.mermaidDiagram.classList.add('dragging');
            }
            document.body.style.cursor = 'grabbing';
            event.preventDefault();
        };

        if (window.PointerEvent) {
            wrapper.addEventListener('pointerdown', (event) => {
                if (event.button !== 0) {
                    return;
                }
                startDragging(event, event.pointerId);
            });

            window.addEventListener('pointermove', (event) => {
                if (!this.isDragging || event.pointerId !== this.activePointerId) {
                    return;
                }

                const deltaX = event.clientX - startX;
                const deltaY = event.clientY - startY;
                this.offsetX += deltaX;
                this.offsetY += deltaY;
                startX = event.clientX;
                startY = event.clientY;
                updateTransform();
            });

            window.addEventListener('pointerup', stopDragging);
            window.addEventListener('pointercancel', stopDragging);
        } else {
            wrapper.addEventListener('mousedown', (event) => {
                if (event.button !== 0) {
                    return;
                }
                startDragging(event, null);
            });

            window.addEventListener('mousemove', (event) => {
                if (!this.isDragging) {
                    return;
                }

                const deltaX = event.clientX - startX;
                const deltaY = event.clientY - startY;
                this.offsetX += deltaX;
                this.offsetY += deltaY;
                startX = event.clientX;
                startY = event.clientY;
                updateTransform();
            });

            window.addEventListener('mouseup', stopDragging);
        }

        window.addEventListener('blur', () => {
            if (this.isDragging) {
                stopDragging();
            }
        });
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
            toggleButton.innerHTML = this.zoomRelativeToCursor ? this.svg_zoom_mouse_rel : this.svg_zoom_orig_rel;
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
            wrapToggleButton.innerHTML = this.isWrapped ? this.svg_table_text_wrap : this.svg_table_text_nowrap;
        });
    }

    setupTextNewlineDelimToggle() {
        const delimToggleButton = this.shadowRoot.querySelector('.newline_delim');

        delimToggleButton.addEventListener('click', () => {
            this.querySelectorAll("tr").forEach(cell => {
                if (!this.br_hidden) {
                    cell.innerHTML = cell.innerHTML.replace(/<br\s*\/?>/g, "; <!--<br>-->");
                } else {
                    cell.innerHTML = cell.innerHTML.replace(/; <\!--<br>-->/g, "<br>");
                }
                delimToggleButton.innerHTML = this.br_hidden ? this.svg_delim_br : this.svg_delim_semicol;
            });
            this.br_hidden = !this.br_hidden;
        });

        // manual button click to set initial state
        delimToggleButton.click();
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
        position: relative; /* Ensures it's stackable */
        // z-index: 1; /* Lower than #diag-top-right-controls */
    }

    mermaid-table-standard .mermaid,
    mermaid-table-standard .mermaid * {
        cursor: grab;
        user-select: none;
        -webkit-user-select: none;
    }

    mermaid-table-standard .mermaid .node,
    mermaid-table-standard .mermaid .node *,
    mermaid-table-standard .mermaid .cluster,
    mermaid-table-standard .mermaid .cluster *,
    mermaid-table-standard .mermaid .nodeLabel {
        cursor: pointer;
    }

    mermaid-table-standard.dragging .mermaid,
    mermaid-table-standard.dragging .mermaid * {
        cursor: grabbing !important;
    }

    .highlighted {
        background: var(--highlight-color) !important;
    }

    tr:nth-child(even) { background: var(--primary-background) }
    tr:nth-child(odd) { background: var(--primary-accent) }

    th {
        cursor: pointer;
    }
    th, td {
        text-align: left;
        vertical-align: top; /* Top align */
        white-space: nowrap;
    }

    table thead th { background: var(--primary-background); position: sticky; top: 0; z-index: 1; }

`;
document.head.appendChild(style);

customElements.define('mermaid-table-standard', TableStandardFmt);


function bindSubgraphClicks(callback, pattern = null, options = {}) {
    const component = options.component
        || document.querySelector('body > mermaid-table-standard')
        || document.querySelector('mermaid-table-standard');

    const bindNow = () => {
        const labels = document.querySelectorAll('.nodeLabel');
        let boundCount = 0;

        labels.forEach((label) => {
            // get class node if label within it's hierarchy or otherwise get class cluster
            const node = label.closest('.node') || label.closest('.cluster');
            if (!node) {
                return; // skip if no node or cluster found
            }
            var text = label.textContent.trim() || '';

            if (!text) {
                return;
            }

            // Check if pattern matches (if pattern is provided)
            if (pattern !== null) {
                const match = text.match(pattern);
                if (!match) return; // Skip nodes without a match
                text = match[1];
            }

            if (node.dataset.subgraphClickBound === 'true') {
                return;
            }

            node.dataset.subgraphClickBound = 'true';
            node.style.cursor = 'pointer';
            node.addEventListener('click', () => {
                if (typeof callback === 'function') {
                    console.log(`Subgraph clicked: ${text}`);
                    callback(text);
                }
            });
            boundCount += 1;
        });

        return boundCount;
    };

    if (bindNow() > 0) {
        return;
    }

    if (!component) {
        return;
    }

    const renderHandler = () => {
        bindNow();
    };

    // Defer until Mermaid finishes rendering if labels are not available yet.
    component.addEventListener('mermaidRendered', renderHandler, { once: true });
}