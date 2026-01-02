"""
Project management routes for DBGear Editor.
Handles project switching, adding, and listing operations.
"""

from pathlib import Path
from fasthtml.common import *
from monsterui.all import *

from ..project import (
    get_current_project, 
    get_recent_projects, 
    switch_project, 
    add_recent_project,
    remove_recent_project
)


def project_list_items(projects, current_path):
    """Generate project list items."""
    if not projects:
        return [Div(
            P("No recent projects", cls="text-gray-500 text-center py-8"),
            cls="border border-gray-200 rounded"
        )]
    
    items = []
    for project in projects:
        # Create switch button or current indicator
        if project["path"] == current_path:
            switch_element = Button(
                "Current",
                cls="px-3 py-1 text-xs rounded mr-2 bg-gray-300 text-gray-500 cursor-not-allowed",
                disabled=True
            )
        else:
            switch_element = Form(
                Button(
                    "Switch",
                    type="submit",
                    cls="px-3 py-1 text-xs rounded mr-2 bg-green-500 text-white hover:bg-green-600"
                ),
                Input(type="hidden", name="selected_project", value=project["path"]),
                method="POST",
                action="/api/projects/switch-simple",
                style="display: inline"
            )
        
        # Create project item
        item = Div(
            Div(
                Div(
                    Strong(project["name"], cls="text-sm font-medium text-gray-900"),
                    P(project["path"], cls="text-xs text-gray-500 mt-1"),
                    cls="flex-1"
                ),
                Div(
                    Span("Current", cls="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded mr-2") if project["path"] == current_path else None,
                    switch_element,
                    Form(
                        Button(
                            "Delete",
                            type="submit",
                            cls="px-3 py-1 text-xs bg-red-500 text-white rounded hover:bg-red-600",
                            onclick="return confirm('Remove this project from the list?')"
                        ),
                        Input(type="hidden", name="project_path", value=project["path"]),
                        method="POST",
                        action="/api/projects/remove-simple",
                        style="display: inline"
                    ),
                    cls="flex items-center"
                ),
                cls="flex justify-between items-center p-4 border border-gray-200 rounded hover:bg-gray-50 mb-2"
            )
        )
        items.append(item)
    
    return items


def register_project_routes(rt):
    """Register all project management routes."""

    @rt("/api/projects/switch-simple", methods=["POST"])
    def switch_project_simple(selected_project: str):
        """Simple project switching via form submission."""
        from starlette.responses import RedirectResponse
        
        if selected_project and selected_project != "":
            success = switch_project(selected_project)
            if success:
                # Redirect back to current page or dashboard
                return RedirectResponse(url="/", status_code=302)
        
        # If switch failed, redirect to dashboard
        return RedirectResponse(url="/", status_code=302)

    @rt("/projects/add")
    def add_project_page():
        """Project management page with add and list functionality."""
        from ..layout import layout, content_header
        from pathlib import Path
        
        # Get current projects for listing
        projects = get_recent_projects()
        current = get_current_project()
        current_path = current.project_path if current and current.is_loaded() else None
        
        content = Div(
            content_header("Project Management", "Add new projects and manage your project list"),
            
            # Add New Project Section
            Div(
                H3("Add New Project", cls="text-lg font-semibold text-gray-900 mb-4"),
                Form(
                    Div(
                        P("Project Directory Path:", cls="text-sm font-medium text-gray-700 mb-2"),
                        Input(
                            type="text",
                            name="project_path",
                            placeholder="/path/to/your/dbgear/project",
                            required=True,
                            cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        ),
                        P("Enter the full path to a directory containing a project.yaml file. The project will be added and switched to immediately.", 
                          cls="mt-1 text-xs text-gray-500"),
                        cls="mb-4"
                    ),
                    
                    Div(
                        Button(
                            "Add & Switch Project",
                            type="submit",
                            cls="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 mr-2"
                        ),
                        A(
                            "Cancel",
                            href="/",
                            cls="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400"
                        ),
                        cls="flex space-x-2"
                    ),
                    
                    method="POST",
                    action="/api/projects/add-simple"
                ),
                cls="bg-white p-6 rounded-lg shadow mb-8"
            ),
            
            # Current Projects List Section
            Div(
                H3("Recent Projects", cls="text-lg font-semibold text-gray-900 mb-4"),
                *project_list_items(projects, current_path),
                cls="bg-white p-6 rounded-lg shadow"
            )
        )
        
        return layout(content, "Project Management")

    @rt("/api/projects/add-simple", methods=["POST"])
    def add_project_simple(project_path: str):
        """Simple project addition via form submission - always switches."""
        from starlette.responses import RedirectResponse
        
        print(f"DEBUG: Add project - path: {project_path}")
        
        if not project_path:
            print("ERROR: No project path provided")
            return RedirectResponse(url="/projects/add", status_code=302)
        
        # Validate path exists and is a valid project
        project_dir = Path(project_path)
        if not project_dir.exists():
            print(f"ERROR: Directory does not exist: {project_path}")
            return RedirectResponse(url="/projects/add", status_code=302)
        
        if not (project_dir / "project.yaml").exists():
            print(f"ERROR: project.yaml not found in: {project_path}")
            return RedirectResponse(url="/projects/add", status_code=302)
        
        # Always add to recent projects and switch
        project_name = project_dir.name
        add_result = add_recent_project(project_path, project_name)
        print(f"DEBUG: Add to recent projects result: {add_result}")
        
        # Switch to the project
        print(f"DEBUG: Attempting to switch to project: {project_path}")
        success = switch_project(project_path)
        print(f"DEBUG: Switch result: {success}")
        
        if success:
            print("SUCCESS: Project added and switched successfully")
            return RedirectResponse(url="/", status_code=302)
        else:
            print("ERROR: Failed to switch project")
            return RedirectResponse(url="/projects/add", status_code=302)


    @rt("/api/projects/remove-simple", methods=["POST"])
    def remove_project_simple(project_path: str):
        """Remove project from recent list via form submission."""
        from starlette.responses import RedirectResponse
        
        print(f"DEBUG: Remove project: {project_path}")
        
        if project_path:
            remove_recent_project(project_path)
            print(f"SUCCESS: Removed project: {project_path}")
        
        return RedirectResponse(url="/projects/add", status_code=302)

    @rt("/api/projects")
    def get_projects():
        """Get list of recent projects."""
        try:
            projects = get_recent_projects()
            current = get_current_project()
            current_path = current.project_path if current else None
            
            return {
                "success": True,
                "current_project": current_path,
                "recent_projects": projects
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @rt("/api/projects/switch", methods=["POST"])
    async def switch_project_api(request):
        """Switch to a different project."""
        try:
            import json
            body = await request.body()
            data = json.loads(body)
            project_path = data.get("project_path")
            
            if not project_path:
                return {
                    "success": False,
                    "error": "project_path is required"
                }
            
            if switch_project(project_path):
                return {
                    "success": True,
                    "message": "Project switched successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to switch project"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @rt("/api/projects/add", methods=["POST"])
    async def add_project_api(request):
        """Add a project to recent projects."""
        try:
            import json
            body = await request.body()
            data = json.loads(body)
            project_path = data.get("project_path")
            project_name = data.get("project_name")
            switch_to_project = data.get("switch", False)
            
            if not project_path:
                return {
                    "success": False,
                    "error": "project_path is required"
                }
            
            # Validate path exists and is a valid project
            project_dir = Path(project_path)
            if not project_dir.exists():
                return {
                    "success": False,
                    "error": "Directory does not exist"
                }
            
            if not (project_dir / "project.yaml").exists():
                return {
                    "success": False,
                    "error": "Not a valid DBGear project (project.yaml not found)"
                }
            
            if switch_to_project:
                # Switch to the project
                if switch_project(project_path):
                    return {
                        "success": True,
                        "message": "Project added and switched successfully"
                    }
                else:
                    return {
                        "success": False,
                        "error": "Failed to switch to project"
                    }
            else:
                # Just add to recent projects
                if add_recent_project(project_path, project_name):
                    return {
                        "success": True,
                        "message": "Project added to recent projects"
                    }
                else:
                    return {
                        "success": False,
                        "error": "Failed to add project"
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @rt("/api/projects/remove", methods=["POST"])
    async def remove_project_api(request):
        """Remove a project from recent projects."""
        try:
            import json
            body = await request.body()
            data = json.loads(body)
            project_path = data.get("project_path")
            
            if not project_path:
                return {
                    "success": False,
                    "error": "project_path is required"
                }
            
            remove_recent_project(project_path)
            return {
                "success": True,
                "message": "Project removed from recent projects"
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

