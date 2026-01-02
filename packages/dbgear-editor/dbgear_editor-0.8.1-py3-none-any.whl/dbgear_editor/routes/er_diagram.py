"""
ER diagram route handlers for DBGear Editor.
"""

from fasthtml.common import *
from starlette.responses import Response

from ..project import get_current_project
from ..components.er_diagram import generate_er_diagram_svg


def register_er_diagram_routes(rt):
    """Register ER diagram-related routes."""

    @rt('/api/er-diagram/{schema_name}/{table_name}')
    def er_diagram_svg(
        schema_name: str,
        table_name: str,
        ref_level: int = 1,
        fk_level: int = 1
    ):
        """
        Generate ER diagram SVG for a specific table.

        Args:
            schema_name: Name of the schema
            table_name: Name of the table to center the diagram on
            ref_level: Levels of referencing tables to include (default: 1)
            fk_level: Levels of referenced tables to include (default: 1)

        Returns:
            SVG response with image/svg+xml content type

        Raises:
            500 error if generation fails
        """
        project = get_current_project()

        if not project or not project.is_loaded():
            raise HTTPException(status_code=404, detail="No project loaded")

        # Get schema manager from project
        schema_manager = project.schema_manager

        # Generate SVG (will raise exception on error -> 500)
        svg_content = generate_er_diagram_svg(
            schema_manager,
            schema_name,
            table_name,
            ref_level,
            fk_level
        )

        # Return SVG response
        return Response(
            content=svg_content,
            media_type="image/svg+xml",
            headers={
                "Cache-Control": "no-cache"
            }
        )
