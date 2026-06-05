"""Downloads folder sorter

This script iterates through the files in a user's downloads folder on Windows and places each file in its appropriate
folder.

This file contains the following functions:

    * move_file - checks if the destination folder exists, creates it if it doesn't, then moves a file into it
    * sort_folder - iterates through the files in the folder
"""

import shutil
from pathlib import Path
import json
import sys
import argparse

def get_download_folder_path():
    """Gets the path to the downloads folder from the command line arguments, or defaults to the user's downloads folder
    if no argument is provided.
    Returns
    -------
    Path
        the path to the downloads folder
    """
    parser = argparse.ArgumentParser(description='Sort files in a specified folder.')
    parser.add_argument('folder', nargs='?', default=str(Path.home() / 'Downloads'), help='the path to the folder to be organized (default: user\'s Downloads folder)')
    
    args = parser.parse_args()

    # Check if the specified folder exists
    if not Path(args.folder).exists():
        print(f"Error: The specified folder '{args.folder}' does not exist.")
        sys.exit(1)
    
    # Check if the specified folder is a directory
    if not Path(args.folder).is_dir():
        print(f"Error: The specified path '{args.folder}' is not a directory.")
        sys.exit(1)

    # If there are no arguments, tell the user that its using the default downloads folder
    if not args.folder:
        print(f"Using default downloads folder: {Path.home() / 'Downloads'}")
        args.folder = str(Path.home() / 'Downloads')

    return Path(args.folder)

def move_file(file, destination):
    """Checks if the destination folder exists, creates it if it doesn't, then moves a file into it
    Parameters
    ----------
    file : Path
        the path to a file
    destination : Path
        the path to the destination folder
    """
    try:
        if not destination.exists():
            destination.mkdir(parents=True, exist_ok=True)
        shutil.move(file, destination)
    except shutil.Error as e:
        print(e)


def sort_folder(folder_path, extensions_map=None, category_names=None, root_path=None):
    """Iterates through the files in the folder recursively, sorting them into sub-folders by extension.
    Parameters
    ----------
    folder_path : Path
        the path to the folder to be organized
    extensions_map : dict
        the mapping of file extensions to folder names (loaded from config.json)
    category_names : set
        the set of category folder names to avoid recursing into
    root_path : Path
        the root folder path where category folders should be created
    """
    # Load config only on first call
    if extensions_map is None:
        with open('config.json', encoding='utf-8') as f:
            categories = json.load(f)

        extensions_map = {}
        category_names = set()
        for category in categories:
            folder_name = category['name']
            category_names.add(folder_name)
            for extension in category['extensions']:
                extensions_map[extension] = folder_name
        
        root_path = folder_path

    # Get all items in the current folder
    items = list(folder_path.iterdir())
    
    for item in items:
        if item.is_file() and not item.name.startswith('.'):
            # Determine the correct destination folder (always at root level)
            destination_folder = extensions_map.get(item.suffix, 'Other')
            correct_destination = root_path.joinpath(destination_folder)
            
            # Move file if it's not already in the correct location
            if item.parent != correct_destination:
                move_file(item, correct_destination)
        elif item.is_dir() and not item.name.startswith('.') and item.name not in category_names:
            # Recursively sort subdirectories (but not the category folders themselves)
            sort_folder(item, extensions_map, category_names, root_path)


if __name__ == '__main__':
    downloads_path = get_download_folder_path()
    sort_folder(downloads_path)
