import os
import sys
from pathlib import Path

def show_structure(root_path="."):
    """Display complete project structure with file sizes"""
    root = Path(root_path)
    
    print("=" * 60)
    print(f"PROJECT STRUCTURE: {root.absolute()}")
    print("=" * 60)
    
    python_files = []
    other_files = []
    
    # Walk through all files
    for file_path in root.rglob("*"):
        if file_path.is_file():
            # Skip .git directory
            if ".git" in str(file_path):
                continue
            
            # Get relative path
            rel_path = file_path.relative_to(root)
            
            # Get size
            size = file_path.stat().st_size
            
            if file_path.suffix == ".py":
                python_files.append((rel_path, size))
            else:
                other_files.append((rel_path, size))
    
    # Sort files
    python_files.sort()
    other_files.sort()
    
    print("\n🐍 PYTHON FILES:")
    print("-" * 60)
    for path, size in python_files:
        size_str = f"{size:,}b" if size > 0 else "Empty"
        print(f"  📄 {path} ({size_str})")
    
    print("\n📄 OTHER FILES:")
    print("-" * 60)
    for path, size in other_files:
        size_str = f"{size:,}b" if size > 0 else "Empty"
        print(f"  📄 {path} ({size_str})")
    
    # Show summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY:")
    print(f"  Total Python files: {len(python_files)}")
    print(f"  Total other files: {len(other_files)}")
    print(f"  Total files: {len(python_files) + len(other_files)}")
    
    # Check critical files
    print("\n🔍 CRITICAL FILES CHECK:")
    critical_files = [
        "main.py",
        "requirements.txt",
        "config/database_config.py",
        "services/expense_service.py",
        "services/export_service.py",
        "visualization/chart_service.py",
        "utils/validation.py"
    ]
    
    for file in critical_files:
        file_path = root / file
        if file_path.exists():
            size = file_path.stat().st_size
            status = "✅" if size > 100 else "⚠️"
            print(f"  {status} {file} ({size:,}b)")
        else:
            print(f"  ❌ {file} (MISSING)")
    
    return python_files

if __name__ == "__main__":
    python_files = show_structure()
    
    # Optionally show first few lines of key files
    print("\n" + "=" * 60)
    print("📝 SAMPLE CODE PREVIEWS:")
    
    key_files = [
        "main.py",
        "config/database_config.py", 
        "services/expense_service.py"
    ]
    
    for file in key_files:
        file_path = Path(file)
        if file_path.exists():
            print(f"\n📄 {file}:")
            print("-" * 40)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[:10]  # First 10 lines
                    for line in lines:
                        print(f"  {line.rstrip()}")
                if len(lines) >= 10:
                    print("  ...")
            except:
                print("  Could not read file")