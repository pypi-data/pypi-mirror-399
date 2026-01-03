#!/usr/bin/env python3
"""
nocd - Run commands in directories without cd
Searches predefined locations for directory by name and executes command there.
"""

import argparse
import os
import sys
import subprocess
from pathlib import Path
import json

CONFIG_FILE = Path.home() / ".nocd_config.json"

DEFAULT_SEARCH_PATHS = [
    str(Path.home()),
    str(Path.home() / "Projects"),
    str(Path.home() / "Code"),
    str(Path.home() / "dev"),
    str(Path.home() / "work"),
    "/opt",
    "/usr/local",
    str(Path.cwd())
]

def load_config():
    """Load configuration with search paths"""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                config = json.load(f)
                return config.get("search_paths", DEFAULT_SEARCH_PATHS)
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    return DEFAULT_SEARCH_PATHS

def save_config(search_paths):
    """Save configuration"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump({"search_paths": search_paths}, f, indent=2)

def find_directory(name, search_paths, max_depth=3):
    """Find directory by name in search paths"""
    candidates = []
    
    for search_path in search_paths:
        search_path = Path(search_path).expanduser()
        if not search_path.exists():
            continue
            
        # Search at multiple depth levels
        for depth in range(max_depth + 1):
            if depth == 0:
                # Check if search_path itself matches
                if search_path.name == name:
                    candidates.append(search_path)
            else:
                # Search at specific depth
                pattern = '/'.join(['*'] * depth)
                try:
                    for candidate in search_path.glob(pattern):
                        if candidate.is_dir() and candidate.name == name:
                            candidates.append(candidate)
                except (PermissionError, OSError):
                    continue
    
    # Remove duplicates and sort by depth (shallower first)
    candidates = list(dict.fromkeys(candidates))
    candidates.sort(key=lambda x: len(x.parts))
    
    return candidates

def run_command_in_directory(directory, command_args):
    """Run command in the specified directory"""
    original_cwd = Path.cwd()
    try:
        os.chdir(directory)
        print(f"📁 Running in: {directory}")
        print(f"🚀 Command: {' '.join(command_args)}")
        
        result = subprocess.run(command_args)
        return result.returncode
    except FileNotFoundError:
        print(f"Error: Command '{command_args[0]}' not found")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1
    finally:
        os.chdir(original_cwd)

def list_directories(search_paths):
    """List all directories found in search paths"""
    all_dirs = {}
    
    for search_path in search_paths:
        search_path = Path(search_path).expanduser()
        if not search_path.exists():
            continue
            
        print(f"\n📂 {search_path}:")
        try:
            for item in search_path.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    all_dirs[item.name] = item
                    print(f"  {item.name}")
        except (PermissionError, OSError):
            print(f"  (Permission denied)")
    
    return all_dirs

def main():
    parser = argparse.ArgumentParser(description="Run commands in directories without cd")
    parser.add_argument("directory", nargs="?", help="Directory name to search for")
    parser.add_argument("command", nargs="*", help="Command to run in the directory")
    parser.add_argument("--list", "-l", action="store_true", help="List available directories")
    parser.add_argument("--add-dir", metavar="PATH", help="Add a search directory")
    parser.add_argument("--remove-dir", metavar="PATH", help="Remove a search directory")
    parser.add_argument("--show-dirs", action="store_true", help="Show current search directories")
    parser.add_argument("--max-depth", type=int, default=3, help="Maximum search depth (default: 3)")
    
    args = parser.parse_args()
    
    search_paths = load_config()
    
    # Handle configuration commands
    if args.add_dir:
        path = str(Path(args.add_dir).expanduser().resolve())
        if path not in search_paths:
            search_paths.append(path)
            save_config(search_paths)
            print(f"✅ Added search directory: {path}")
        else:
            print(f"❌ Directory already exists: {path}")
        return 0
    
    if args.remove_dir:
        path = str(Path(args.remove_dir).expanduser().resolve())
        if path in search_paths:
            search_paths.remove(path)
            save_config(search_paths)
            print(f"✅ Removed search directory: {path}")
        else:
            print(f"❌ Directory not found: {path}")
        return 0
    
    if args.show_dirs:
        print("🔍 Current search directories:")
        for i, path in enumerate(search_paths, 1):
            exists = "✅" if Path(path).exists() else "❌"
            print(f"  {i}. {path} {exists}")
        return 0
    
    if args.list:
        print("📁 Available directories:")
        list_directories(search_paths)
        return 0
    
    # Main command execution
    if not args.directory:
        parser.print_help()
        return 1
    
    if not args.command:
        print("Error: No command specified")
        print("Usage: nocd <directory> <command> [args...]")
        return 1
    
    # Find the directory
    candidates = find_directory(args.directory, search_paths, args.max_depth)
    
    if not candidates:
        print(f"❌ Directory '{args.directory}' not found in search directories")
        print("Run 'nocd --list' to see available directories or 'nocd --add-dir PATH' to add new search locations")
        return 1
    
    if len(candidates) > 1:
        print(f"🤔 Multiple directories found for '{args.directory}':")
        for i, candidate in enumerate(candidates, 1):
            print(f"  {i}. {candidate}")
        
        try:
            choice = input("Choose directory (1-{}) or press Enter for first: ".format(len(candidates)))
            if choice.strip():
                selected = candidates[int(choice) - 1]
            else:
                selected = candidates[0]
        except (ValueError, IndexError, KeyboardInterrupt):
            print("Using first directory")
            selected = candidates[0]
    else:
        selected = candidates[0]
    
    # Run the command
    return run_command_in_directory(selected, args.command)

if __name__ == "__main__":
    sys.exit(main())