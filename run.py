# run.py
"""
Daily Expense Tracker - Application Launcher
Provides selection between CLI and GUI interfaces
"""

import os
import sys

# Add project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def clear_screen():
    """Clear the terminal screen"""
    os.system("cls" if os.name == "nt" else "clear")


def show_banner():
    """Display application banner and main menu"""
    clear_screen()
    print("=" * 60)
    print("  💰 DAILY EXPENSE TRACKER".center(60))
    print("=" * 60)
    print()
    print("Select the mode to run:")
    print()
    print("  [1] CLI Mode (Command Line Interface)")
    print("  [2] GUI Mode (Graphical User Interface)")
    print("  [3] Exit")
    print()
    print("=" * 60)


def run_cli():
    """Execute the CLI version of the application"""
    try:
        from cli import main
        main()
    except ImportError as e:
        print(f"❌ Error: {e}")
        print("Ensure main.py exists and dependencies are installed.")
        input("\nPress Enter to continue...")
    except Exception as e:
        print(f"❌ Error: {e}")
        input("\nPress Enter to continue...")


def run_gui():
    """Execute the GUI version of the application"""
    try:
        import tkinter as tk
        from gui import main as gui_main
        gui_main()
    except ImportError as e:
        print(f"❌ Error: {e}")
        print("Ensure gui.py exists and tkinter is installed.")
        input("\nPress Enter to continue...")
    except Exception as e:
        print(f"❌ Error: {e}")
        input("\nPress Enter to continue...")


def main():
    """Main launcher function"""
    while True:
        show_banner()
        
        choice = input("Select mode (1/2/3): ").strip()
        
        if choice == "1":
            run_cli()
            continue
        elif choice == "2":
            run_gui()
            continue
        elif choice == "3":
            print("\n👋 Thank you! Goodbye!")
            break
        else:
            print("\n❌ Invalid selection. Please choose 1, 2, or 3.")
            input("\nPress Enter to continue...")
            continue


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Thank you! Goodbye!")
        sys.exit(0)