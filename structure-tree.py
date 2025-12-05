# daily-expense-tracker/structure-tree.py

"""
Simple project structure viewer - EXCLUDES VENV AND CACHE
"""

import os
import sys

def print_tree(start_path=".", max_depth=None, show_hidden=False):
    """
    Print directory tree structure

    Args:
        start_path (str): Starting directory path
        max_depth (int): Maximum depth to display
        show_hidden (bool): Whether to show hidden files/folders
    """
    start_path = os.path.abspath(start_path)

    def should_skip(name):
        """Check if item should be skipped"""
        if not show_hidden and name.startswith("."):
            return True
        if name in ["__pycache__", ".git", "venv", ".venv", "env", ".env"]:
            return True
        return False

    def print_item(path, prefix, is_last):
        """Print a single item with proper prefix"""
        name = os.path.basename(path)

        # Skip hidden/system directories
        if should_skip(name):
            return

        # Choose connector
        if is_last:
            connector = "└── "
            next_prefix = prefix + "    "
        else:
            connector = "├── "
            next_prefix = prefix + "│   "

        # Check if it's a directory or file
        if os.path.isdir(path):
            print(f"{prefix}{connector}{name}/")
            return next_prefix, True
        else:
            print(f"{prefix}{connector}{name}")
            return next_prefix, False

    def walk_directory(current_path, prefix="", depth=0):
        """Recursively walk through directory"""
        if max_depth is not None and depth > max_depth:
            return

        try:
            items = os.listdir(current_path)
        except PermissionError:
            print(f"{prefix}└── [Permission Denied]")
            return

        # Filter and sort items
        items = [item for item in items if not should_skip(item)]
        items.sort(key=lambda x: (not os.path.isdir(os.path.join(current_path, x)), x.lower()))

        # Print all items
        for i, item in enumerate(items):
            full_path = os.path.join(current_path, item)
            is_last = i == len(items) - 1

            next_prefix, is_dir = print_item(full_path, prefix, is_last)

            # Recursively process directories
            if is_dir:
                walk_directory(full_path, next_prefix, depth + 1)

    print(f"\n📁 Directory Tree: {os.path.basename(start_path)}/")
    print("─" * 50)
    walk_directory(start_path)

if __name__ == "__main__":
    # Parse command line arguments
    start_path = "."
    max_depth = None
    show_hidden = False

    for arg in sys.argv[1:]:
        if arg.startswith("--depth="):
            try:
                max_depth = int(arg.split("=")[1])
            except ValueError:
                pass
        elif arg == "--hidden":
            show_hidden = True
        elif os.path.isdir(arg):
            start_path = arg

    print_tree(start_path, max_depth, show_hidden)
    print()
