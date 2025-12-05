# project portofolio/junior projects/daily-expense-tracker/generate/file_and_folder.py

"""
File Structure Generator for daily-expense-tracker
"""

from pathlib import Path

def main():
    print("Creating daily-expense-tracker file and folder structure...\n")
    # Project folder
    project = Path("daily-expense-tracker")
    # Create folders
    folders = [
        "config",
        "models",
        "services",
        "utils",
        "visualization",
        "tests",
        "data",
        "exports",
        "docs",
        "generate",
        "charts",
    ]
    # Create files
    files = [
        # Config
        "config/__init__.py",
        "config/database_config.py",
        # Generate
        "generate/file_and_folder.py",
        "generate/structure.py",
        "generate/sample_data.py",
        "generate/database_schema.py",
        "generate/documentation.py",
        # Docs
        "docs/README.md",
        "docs/project_plan.md",
        "docs/usage.md",
        "docs/development.md",
        "docs/testing.md",
        "docs/deployment.md",
        # Models
        "models/__init__.py",
        "models/expense_model.py",
        "models/category_model.py",
        # Services
        "services/__init__.py",
        "services/database_service.py",
        "services/expense_service.py",
        "services/export_service.py",
        "services/analysis_service.py",
        # Utils
        "utils/__init__.py",
        "utils/validation.py",
        "utils/date_utils.py",
        "utils/formatters.py",
        "utils/exceptions.py",
        # Visualization
        "visualization/__init__.py",
        "visualization/chart_service.py",
        # Tests
        "tests/__init__.py",
        "tests/test_database.py",
        "tests/test_expenses.py",
        "tests/test_export.py",
        "tests/conftest.py",
        # Root files
        "__init__.py",
        "main.py",
        "run.py",
        "requirements.txt",
        "README.md",
        ".gitignore",
        "pyproject.toml",
        # Empty dir markers
        "data/.gitkeep",
        "exports/.gitkeep",
        "charts/.gitkeep",
    ]
    # Create project folder
    project.mkdir(exist_ok=True)
    # Create all folders
    for folder in folders:
        (project / folder).mkdir(parents=True, exist_ok=True)
        print(f"Created folder: {folder}/")
    # Create all files (empty)
    for file in files:
        file_path = project / file
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.touch()
        print(f"Created file:   {file}")
    print(f"\nDone! Created project at: {project.absolute()}")
    # Show tree
    show_tree(project)

def show_tree(path: Path, prefix: str = ""):
    """Show directory tree"""
    items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
    for i, item in enumerate(items):
        # Skip some files in display
        if item.name == ".gitkeep":
            continue
        is_last = i == len(items) - 1
        connector = "└── " if is_last else "├── "
        # Show folder with /
        if item.is_dir():
            print(f"{prefix}{connector}{item.name}/")
        else:
            print(f"{prefix}{connector}{item.name}")
        # Recurse into directories
        if item.is_dir():
            extension = "    " if is_last else "│   "
            show_tree(item, prefix + extension)

if __name__ == "__main__":
    main()
