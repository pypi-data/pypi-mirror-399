"""
Table-related route handlers for DBGear Editor.
"""

from fasthtml.common import *
from starlette.requests import Request

from ..layout import layout, content_header, breadcrumb
from ..project import get_current_project
from ..ui.tables import (
    table_info_section, table_columns_section,
    table_indexes_section, table_relations_section
)
from ..components.right_sidebar import table_notes_sidebar


def register_table_routes(rt):
    """Register table-related routes."""

    @rt('/schemas/{schema_name}/tables/{table_name}')
    def table_detail(schema_name: str, table_name: str, request: Request = None):
        """Table detail page showing column definitions and constraints."""
        project = get_current_project()

        if not project or not project.is_loaded():
            return RedirectResponse(url="/")

        schemas = project.get_schemas()
        schema = schemas.get(schema_name)

        if not schema:
            return NotFoundResponse("Schema not found")

        tables = project.get_tables(schema_name).get(schema_name, {})
        table = tables.get(table_name)

        if not table:
            return NotFoundResponse("Table not found")

        content = Div(
            breadcrumb(("Schemas", "/schemas"), (schema_name, f"/schemas/{schema_name}"), table_name),

            content_header(
                f"Table: {table_name}",
                f"Schema: {schema_name}"
            ),

            # ER Diagram section
            Div(
                # Header with controls
                Div(
                    Div(
                        H2("ER Diagram", cls="text-lg font-medium text-gray-900"),
                        Button(
                            "▼",
                            id="er-toggle-btn",
                            onclick="toggleERDiagram()",
                            cls="ml-2 px-2 py-1 text-sm text-gray-600 hover:text-gray-900"
                        ),
                        cls="flex items-center"
                    ),
                    Div(
                        # Zoom controls
                        Div(
                            Button(
                                "−",
                                onclick="zoomERDiagram(-10)",
                                cls="px-3 py-1 bg-gray-200 hover:bg-gray-300 rounded-l text-sm font-medium"
                            ),
                            Button(
                                "+",
                                onclick="zoomERDiagram(10)",
                                cls="px-3 py-1 bg-gray-200 hover:bg-gray-300 rounded-r text-sm font-medium"
                            ),
                            Span(id="zoom-level", cls="ml-2 text-sm text-gray-600"),
                            cls="flex items-center mr-4"
                        ),
                        # Level selection buttons
                        Div(
                            Span("Referenced by:", cls="text-sm text-gray-600 mr-2"),
                            *[
                                Button(
                                    str(level),
                                    onclick=f"changeERLevel({level}, null)",
                                    id=f"ref-level-{level}",
                                    cls=f"px-2 py-1 text-xs {'bg-blue-500 text-white' if level == 1 else 'bg-gray-200 hover:bg-gray-300'} {'rounded-l' if level == 4 else ''} {'rounded-r' if level == 1 else ''}"
                                )
                                for level in [4, 3, 2, 1]
                            ],
                            Span("│", cls="mx-2 text-gray-400"),
                            *[
                                Button(
                                    str(level),
                                    onclick=f"changeERLevel(null, {level})",
                                    id=f"fk-level-{level}",
                                    cls=f"px-2 py-1 text-xs {'bg-blue-500 text-white' if level == 1 else 'bg-gray-200 hover:bg-gray-300'} {'rounded-l' if level == 1 else ''} {'rounded-r' if level == 4 else ''}"
                                )
                                for level in [1, 2, 3, 4]
                            ],
                            Span(":References", cls="text-sm text-gray-600 ml-2"),
                            cls="flex items-center"
                        ),
                        cls="flex items-center",
                        id="er-controls"
                    ),
                    cls="flex justify-between items-center mb-4"
                ),
                # ER Diagram container
                Div(
                    Div(
                        Img(
                            src=f"/api/er-diagram/{schema_name}/{table_name}?ref_level=1&fk_level=1",
                            alt=f"ER Diagram for {table_name}",
                            id="er-diagram-img",
                            cls="w-full h-auto transition-transform duration-200"
                        ),
                        id="er-diagram-container",
                        cls="overflow-auto"
                    ),
                    cls="border border-gray-200 rounded",
                    id="er-content"
                ),
                # JavaScript for interactive controls
                Script(f"""
                    let currentRefLevel = 1;
                    let currentFkLevel = 1;
                    let currentZoom = 100;
                    let erDiagramVisible = true;
                    const schemaName = '{schema_name}';
                    const tableName = '{table_name}';

                    function updateZoomDisplay() {{
                        document.getElementById('zoom-level').textContent = currentZoom + '%';
                    }}

                    function zoomERDiagram(delta) {{
                        currentZoom = Math.max(10, Math.min(200, currentZoom + delta));
                        const img = document.getElementById('er-diagram-img');
                        img.style.transform = `scale(${{currentZoom / 100}})`;
                        img.style.transformOrigin = 'top left';
                        updateZoomDisplay();
                    }}

                    function toggleERDiagram() {{
                        erDiagramVisible = !erDiagramVisible;
                        const content = document.getElementById('er-content');
                        const controls = document.getElementById('er-controls');
                        const toggleBtn = document.getElementById('er-toggle-btn');

                        if (erDiagramVisible) {{
                            content.style.display = 'block';
                            controls.style.display = 'flex';
                            toggleBtn.textContent = '▼';
                        }} else {{
                            content.style.display = 'none';
                            controls.style.display = 'none';
                            toggleBtn.textContent = '▲';
                        }}
                    }}

                    function changeERLevel(refLevel, fkLevel) {{
                        if (refLevel !== null) {{
                            currentRefLevel = refLevel;
                            // Update button styles for ref levels
                            for (let i = 1; i <= 4; i++) {{
                                const btn = document.getElementById(`ref-level-${{i}}`);
                                if (i === refLevel) {{
                                    btn.className = btn.className.replace('bg-gray-200 hover:bg-gray-300', 'bg-blue-500 text-white');
                                }} else {{
                                    btn.className = btn.className.replace('bg-blue-500 text-white', 'bg-gray-200 hover:bg-gray-300');
                                }}
                            }}
                        }}
                        if (fkLevel !== null) {{
                            currentFkLevel = fkLevel;
                            // Update button styles for fk levels
                            for (let i = 1; i <= 4; i++) {{
                                const btn = document.getElementById(`fk-level-${{i}}`);
                                if (i === fkLevel) {{
                                    btn.className = btn.className.replace('bg-gray-200 hover:bg-gray-300', 'bg-blue-500 text-white');
                                }} else {{
                                    btn.className = btn.className.replace('bg-blue-500 text-white', 'bg-gray-200 hover:bg-gray-300');
                                }}
                            }}
                        }}

                        // Update image source
                        const img = document.getElementById('er-diagram-img');
                        img.src = `/api/er-diagram/${{schemaName}}/${{tableName}}?ref_level=${{currentRefLevel}}&fk_level=${{currentFkLevel}}`;
                    }}

                    // Initialize zoom display
                    updateZoomDisplay();
                """),
                cls="bg-white shadow rounded-lg p-6 mb-6"
            ),

            # Table information card
            Div(
                H2("Table Information", cls="text-lg font-medium text-gray-900 mb-4"),
                table_info_section(table, schema_name, table_name),
                cls="bg-white shadow rounded-lg p-6 mb-6"
            ),

            # Columns section
            Div(
                H2("Columns", cls="text-lg font-medium text-gray-900 mb-4"),
                table_columns_section(table),
                cls="bg-white shadow rounded-lg p-6 mb-6"
            ),

            # Indexes section (if any)
            *([
                Div(
                    H2("Indexes", cls="text-lg font-medium text-gray-900 mb-4"),
                    table_indexes_section(table),
                    cls="bg-white shadow rounded-lg p-6 mb-6"
                )
            ] if len(list(table.indexes)) > 0 else []),

            # Relations section (if any)
            *([
                Div(
                    H2("Relations", cls="text-lg font-medium text-gray-900 mb-4"),
                    table_relations_section(table),
                    cls="bg-white shadow rounded-lg p-6 mb-6"
                )
            ] if len(list(table.relations)) > 0 else []),

        )

        # Create right sidebar with notes
        sidebar_content = table_notes_sidebar(table)

        return layout(
            content, 
            "Table Details", 
            str(request.url.path) if request else "",
            sidebar_content,
            schema_name=schema_name,
            table_name=table_name
        )
