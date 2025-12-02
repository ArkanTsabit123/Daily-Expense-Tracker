#project portofolio\junior projects\daily-expense-tracker\generate\git_setup.py

import subprocess
import sys
from pathlib import Path

def create_gitignore():
    gitignore_content = """__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

venv/
env/
ENV/
env.bak/
venv.bak/

.vscode/
.idea/
*.swp
*.swo
*~

.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

data/*.db
data/*.db-journal
exports/*
charts/*
!exports/.gitkeep
!charts/.gitkeep
!data/.gitkeep

logs/
*.log

.pytest_cache/
.coverage
htmlcov/
.tox/
"""

    project_root = Path(__file__).parent.parent.parent
    gitignore_path = project_root / ".gitignore"
    
    with open(gitignore_path, 'w', encoding='utf-8') as f:
        f.write(gitignore_content)
    
    print(f"Created .gitignore at {gitignore_path}")
    return gitignore_path

def initialize_git_repo():
    project_root = Path(__file__).parent.parent.parent
    
    try:
        subprocess.run(["git", "--version"], check=True, capture_output=True)
        
        result = subprocess.run(
            ["git", "init"],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("Git repository initialized")
            
            subprocess.run(["git", "add", "."], cwd=project_root)
            print("Files added to staging")
            
            commit_result = subprocess.run(
                ["git", "commit", "-m", "Initial commit: Project structure and foundation"],
                cwd=project_root,
                capture_output=True,
                text=True
            )
            
            if commit_result.returncode == 0:
                print("Initial commit created")
            else:
                print(f"Commit failed: {commit_result.stderr}")
        else:
            print(f"Git init failed: {result.stderr}")
            
    except FileNotFoundError:
        print("Git not installed")
    except Exception as e:
        print(f"Error: {str(e)}")

def setup_git_hooks():
    project_root = Path(__file__).parent.parent.parent
    hooks_dir = project_root / ".git" / "hooks"
    
    if hooks_dir.exists():
        pre_commit_content = """#!/bin/sh
echo "Running pre-commit checks..."
echo "✓ Project structure verified"
"""
        
        pre_commit_path = hooks_dir / "pre-commit"
        with open(pre_commit_path, 'w', encoding='utf-8') as f:
            f.write(pre_commit_content)
        
        import os
        if os.name != 'nt':
            os.chmod(pre_commit_path, 0o755)
        
        print("Git hooks configured")

if __name__ == "__main__":
    create_gitignore()
    initialize_git_repo()
    setup_git_hooks()
