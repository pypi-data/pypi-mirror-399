# DBGear Editor

FastHTML-based web interface for viewing and managing DBGear projects with dynamic project switching capabilities.

## 🚀 Features

- **Web-based Interface**: Modern FastHTML-powered web UI
- **Dynamic Project Switching**: Switch between multiple DBGear projects without restart
- **Schema Visualization**: View tables, views, procedures, and triggers
- **Dependencies Mapping**: Visualize relationships between database objects
- **Project Management**: Add, switch, and manage multiple projects
- **Persistent Configuration**: Settings saved to `~/.dbgear/editor_config.json`

## 📦 Installation

### From PyPI (when available)

```bash
pip install dbgear-editor
```

### From Source

```bash
git clone <repository>
cd dbgear.feature-editor/packages/dbgear-editor
pip install -e .
```

## 🏃 Usage

### Command Line

```bash
# Start with default project
dbgear-editor

# Specify project directory
dbgear-editor --project /path/to/project

# Custom host and port
dbgear-editor --host 0.0.0.0 --port 8080

# Enable auto-reload for development
dbgear-editor --reload
```

### Web Interface

1. Open `http://localhost:8000` in your browser
2. Use the project dropdown in the header to switch between projects
3. Click the `+` button or navigate to `/projects/add` to add new projects
4. Navigate using the sidebar to explore schemas and database objects

## 🐳 Docker Usage

### Build and Run

```bash
# Build the image
cd packages/dbgear-editor
docker build -t dbgear-editor .

# Run with project directory mounted
docker run -p 8000:8000 \
  -v /path/to/your/projects:/app/data/projects:ro \
  dbgear-editor
```

### With Specific Project

```bash
# Start with a specific project
docker run -p 8000:8000 \
  -v /path/to/project:/app/data/my-project:ro \
  -e PROJECT_PATH=/app/data/my-project \
  dbgear-editor
```

### Persistent Configuration

```bash
# Persist settings across container restarts
docker run -p 8000:8000 \
  -v dbgear-config:/home/dbgear/.dbgear \
  -v /path/to/projects:/app/data/projects:ro \
  dbgear-editor
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PROJECT_PATH` | Auto-load project path on startup | None |
| `PYTHONPATH` | Python module search path | `/app` |

## 🗂️ Project Structure

DBGear Editor expects projects to have the following structure:

```
project-directory/
├── project.yaml          # DBGear project configuration
├── schema.yaml           # Schema definitions
└── data/                 # Optional data files
    ├── schema_name/
    │   └── table_name.dat
    └── ...
```

## ⚙️ Configuration

Settings are automatically saved to `~/.dbgear/editor_config.json`:

```json
{
  "version": "1.0",
  "current_project": "/path/to/current/project",
  "recent_projects": [
    {
      "name": "Project Name",
      "path": "/path/to/project",
      "last_accessed": "2025-01-09T10:30:00Z"
    }
  ]
}
```

## 🔧 Development

### Prerequisites

- Python 3.12+
- Poetry (optional, for dependency management)

### Setup

```bash
# Clone repository
git clone <repository>
cd dbgear.feature-editor

# Install in development mode
cd packages/dbgear-editor
pip install -e .

# Or with poetry
poetry install
```

### Running in Development Mode

```bash
# With auto-reload
dbgear-editor --reload --project /path/to/test/project

# Docker development
docker run -p 8000:8000 \
  -v $(pwd):/app \
  -v /path/to/projects:/app/data/projects:ro \
  dbgear-editor --reload
```

## 🛠️ Troubleshooting

### Common Issues

1. **Project not loading**
   - Ensure `project.yaml` exists in the project directory
   - Check file permissions
   - Verify the project path is correct

2. **Docker permission issues**
   ```bash
   # Run with specific user
   docker run --user $(id -u):$(id -g) -p 8000:8000 dbgear-editor
   ```

3. **Port already in use**
   ```bash
   # Use different port
   dbgear-editor --port 8080
   ```

### Logs and Debugging

```bash
# Check container logs
docker logs <container_id>

# Access container shell
docker exec -it <container_id> bash

# Verbose startup
docker run -p 8000:8000 -e PYTHONUNBUFFERED=1 dbgear-editor
```

## 📝 Version History

### v0.7.0
- ✅ **Dynamic Project Switching**: Switch between projects without restart
- ✅ **Settings Persistence**: Configuration saved automatically to `~/.dbgear/editor_config.json`
- ✅ **Enhanced UI**: MonsterUI Select dropdown with project path display
- ✅ **Project Management**: Dedicated management page at `/projects/add`
- ✅ **Dynamic Page Titles**: Format `schema@table (project_path)` for better tab identification
- ✅ **Clean Architecture**: Removed JavaScript dependencies and Label components
- ✅ **Docker Support**: Single-stage build for development efficiency

### v0.6.0
- FastHTML-based web interface
- Schema visualization
- Dependencies mapping
- 3-pane layout system

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

Copyright (c) 2022 tamuto

See the [LICENSE](../../LICENSE) file for details.

## 🔗 Links

- [DBGear Core](../dbgear/)
- [Documentation](../../docs/)
- [Issue Tracker](../../issues/)
