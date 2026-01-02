"""
Main entry point for DBGear Editor.
A FastHTML-based web interface for viewing and managing DBGear projects.
"""

import argparse
from uuid import uuid4

import uvicorn
from fasthtml.common import *
from monsterui.all import *

from .project import load_project
from .settings import init_settings, get_editor_settings

# Import route registration functions
from .routes.dashboard import register_dashboard_routes
from .routes.tables import register_table_routes
from .routes.views import register_view_routes
from .routes.procedures import register_procedure_routes
from .routes.triggers import register_trigger_routes
from .routes.projects import register_project_routes
from .routes.er_diagram import register_er_diagram_routes

# Initialize FastHTML app
app, rt = fast_app(
    hdrs=[*Theme.blue.headers(highlightjs=True)],
    secret_key=str(uuid4())
)

# Register all routes
register_dashboard_routes(rt)
register_table_routes(rt)
register_view_routes(rt)
register_procedure_routes(rt)
register_trigger_routes(rt)
register_project_routes(rt)
register_er_diagram_routes(rt)

# Test route to verify routing works
@rt('/test-static')
def test_static():
    """Test route to verify routing is working."""
    print("DEBUG: Test static route called!")
    return "Static routing test successful"



def main():
    """Main entry point for the dbgear-editor command."""
    parser = argparse.ArgumentParser(description='DBGear FastHTML Editor')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to (default: 8000)')
    parser.add_argument('--project', default=None, help='Project directory to load')

    args = parser.parse_args()

    # Initialize settings system
    init_settings()

    # Try to load project from settings or command line
    settings = get_editor_settings()
    project_to_load = args.project

    # If no project specified in command line, try to load from settings
    if not project_to_load:
        current_project = settings.get_current_project()
        if current_project:
            project_to_load = current_project

    # Load project if we have a path
    if project_to_load:
        success = load_project(project_to_load)
        if success:
            print(f"✅ Loaded project from: {project_to_load}")
        else:
            print(f"❌ Failed to load project from: {project_to_load}")
            print("⚠️  Starting without a project loaded. Use the web interface to add projects.")
    else:
        # No project to load
        print("ℹ️  No project specified.")

        # If we have recent projects, show them
        recent_projects = settings.get_recent_projects()
        if recent_projects:
            print("\n📋 Recent projects:")
            for project in recent_projects[:5]:
                print(f"   - {project['name']}: {project['path']}")
            print("\nYou can select a project using the web interface.")
        else:
            print("Use 'dbgear-editor --project /path/to/project' to load a project,")
            print("or use the web interface to add projects.")

        print("⚠️  Starting without a project loaded.")

    print(f"🚀 Starting DBGear Editor on http://{args.host}:{args.port}")

    uvicorn.run(
        "dbgear_editor.main:app",
        host=args.host,
        port=args.port
    )


if __name__ == "__main__":
    main()
