"""
Settings management for DBGear Editor.
Handles configuration persistence and project history.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class EditorSettings:
    """DBGear Editor settings management."""
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize settings manager.
        
        Args:
            config_dir: Custom config directory path, defaults to ~/.dbgear
        """
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            self.config_dir = Path.home() / ".dbgear"
        
        self.config_file = self.config_dir / "editor_config.json"
        self.config_dir.mkdir(exist_ok=True)
        
        self._settings = self._load_settings()
    
    def _load_settings(self) -> Dict:
        """Load settings from config file."""
        default_settings = {
            "version": "1.0",
            "current_project": None,
            "recent_projects": []
        }
        
        if not self.config_file.exists():
            return default_settings
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                # Merge with defaults for missing keys
                for key, value in default_settings.items():
                    if key not in settings:
                        settings[key] = value
                return settings
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Failed to load settings: {e}")
            return default_settings
    
    def _save_settings(self):
        """Save settings to config file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Warning: Failed to save settings: {e}")
    
    def get_current_project(self) -> Optional[str]:
        """Get current project path."""
        return self._settings.get("current_project")
    
    def set_current_project(self, project_path: str):
        """
        Set current project and update recent projects list.
        
        Args:
            project_path: Path to the project directory
        """
        self._settings["current_project"] = project_path
        self.add_recent_project(project_path)
        self._save_settings()
    
    def add_recent_project(self, project_path: str, project_name: Optional[str] = None):
        """
        Add or update project in recent projects list.
        
        Args:
            project_path: Path to the project directory
            project_name: Optional project name, will be derived from path if not provided
        """
        if not project_name:
            # Try to extract project name from project.yaml or use directory name
            try:
                from dbgear.models.project import Project
                project = Project.load(project_path)
                project_name = getattr(project, 'project_name', Path(project_path).name)
            except:
                project_name = Path(project_path).name
        
        # Remove existing entry if present
        recent_projects = [p for p in self._settings["recent_projects"] 
                          if p["path"] != project_path]
        
        # Add to beginning of list
        recent_projects.insert(0, {
            "name": project_name,
            "path": project_path,
            "last_accessed": datetime.now().isoformat()
        })
        
        # Keep only last 10 projects
        self._settings["recent_projects"] = recent_projects[:10]
        self._save_settings()
    
    def get_recent_projects(self) -> List[Dict]:
        """Get list of recent projects."""
        return self._settings.get("recent_projects", [])
    
    def remove_recent_project(self, project_path: str):
        """
        Remove project from recent projects list.
        
        Args:
            project_path: Path to the project directory to remove
        """
        self._settings["recent_projects"] = [
            p for p in self._settings["recent_projects"] 
            if p["path"] != project_path
        ]
        
        # If removed project was current, clear current
        if self._settings["current_project"] == project_path:
            self._settings["current_project"] = None
        
        self._save_settings()
    
    def validate_recent_projects(self):
        """Remove projects that no longer exist from recent list."""
        valid_projects = []
        
        for project in self._settings["recent_projects"]:
            project_path = Path(project["path"])
            if project_path.exists() and (project_path / "project.yaml").exists():
                valid_projects.append(project)
        
        if len(valid_projects) != len(self._settings["recent_projects"]):
            self._settings["recent_projects"] = valid_projects
            self._save_settings()
    
    def get_all_settings(self) -> Dict:
        """Get all settings as dictionary."""
        return self._settings.copy()


# Global settings instance
_editor_settings: Optional[EditorSettings] = None


def get_editor_settings() -> EditorSettings:
    """Get the global editor settings instance."""
    global _editor_settings
    if _editor_settings is None:
        _editor_settings = EditorSettings()
    return _editor_settings


def init_settings(config_dir: Optional[str] = None) -> EditorSettings:
    """
    Initialize editor settings with optional custom config directory.
    
    Args:
        config_dir: Custom config directory path
        
    Returns:
        EditorSettings instance
    """
    global _editor_settings
    _editor_settings = EditorSettings(config_dir)
    return _editor_settings