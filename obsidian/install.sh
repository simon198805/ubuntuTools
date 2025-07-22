#!/bin/bash

# install.sh - A script to set up Obsidian snippets.
# This script creates a symbolic link from the current directory's 'snippets' folder
# to the '.obsidian' directory within your specified Obsidian vault.

# --- Help Function ---
show_help() {
  echo "Usage: $0 <OBSIDIAN_VAULT_PATH>"
  echo "       $0 [-h|--help]"
  echo ""
  echo "This script creates a symbolic link for Obsidian snippets."
  echo "It links the 'snippets' directory in the current working directory"
  echo "to the '.obsidian' configuration directory of your Obsidian vault."
  echo ""
  echo "Arguments:"
  echo "  <OBSIDIAN_VAULT_PATH>  The absolute or relative path to your Obsidian vault."
  echo "                       This is the root directory of your vault, not the .obsidian folder itself."
  echo ""
  echo "Options:"
  echo "  -h, --help             Display this help message and exit."
  echo ""
  echo "Examples:"
  echo "  $0 ~/Documents/ObsidianVault"
  echo "  $0 /path/to/my/notes"
  echo ""
  echo "Note: The 'snippets' directory must exist in the current working directory."
  echo "      If it doesn't, please create it before running this script."
}

# --- Main Script Logic ---

# Check for help flags
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
  show_help
  exit 0 # Exit after showing help
fi

# Check if the correct number of arguments is provided.
if [ "$#" -ne 1 ]; then
  echo "Error: Incorrect number of arguments."
  show_help
  exit 1
fi

# Assign the first argument to a descriptive variable.
OBSIDIAN_VAULT_PATH="$1"

# Define the source and destination paths for the symbolic link.
# PWD (Print Working Directory) gives the current directory.
SOURCE_SNIPPETS_DIR="$PWD/snippets"
DEST_OBSIDIAN_DIR="$OBSIDIAN_VAULT_PATH/.obsidian"
DEST_SNIPPETS_LINK="$DEST_OBSIDIAN_DIR/snippets"

# Check if the source 'snippets' directory exists.
if [ ! -d "$SOURCE_SNIPPETS_DIR" ]; then
  echo "Error: Source directory '$SOURCE_SNIPPETS_DIR' not found."
  echo "Please ensure a 'snippets' directory exists in the current location ($PWD)."
  exit 1
fi

# Check if the target Obsidian vault path is a directory.
if [ ! -d "$OBSIDIAN_VAULT_PATH" ]; then
  echo "Error: Obsidian vault path '$OBSIDIAN_VAULT_PATH' is not a valid directory."
  echo "Please provide the correct path to your Obsidian vault."
  exit 1
fi

# Check if the .obsidian directory exists within the vault. If not, create it.
if [ ! -d "$DEST_OBSIDIAN_DIR" ]; then
  echo "'.obsidian' directory not found in '$OBSIDIAN_VAULT_PATH'. Creating it..."
  mkdir -p "$DEST_OBSIDIAN_DIR"
  if [ $? -ne 0 ]; then
    echo "Error: Failed to create directory '$DEST_OBSIDIAN_DIR'."
    exit 1
  fi
fi

# Check if a symbolic link or directory already exists at the destination.
if [ -L "$DEST_SNIPPETS_LINK" ]; then
  echo "Existing symbolic link found at '$DEST_SNIPPETS_LINK'. Removing it..."
  rm "$DEST_SNIPPETS_LINK"
  # Proceed to create the new symbolic link after removing the old one.
elif [ -d "$DEST_SNIPPETS_LINK" ]; then
  echo "A directory already exists at '$DEST_SNIPPETS_LINK'."
  echo "Copying contents from '$SOURCE_SNIPPETS_DIR' into it."
  # Copy all files and directories from source to destination, overwriting existing ones.
  cp -r "$SOURCE_SNIPPETS_DIR"/* "$DEST_SNIPPETS_LINK"/
  if [ $? -eq 0 ]; then
    echo "Contents copied successfully to '$DEST_SNIPPETS_LINK'!"
    echo "Obsidian snippets should now be available in your vault."
    exit 0 # Exit after copying, as symbolic link is not needed
  else
    echo "Error: Failed to copy contents to '$DEST_SNIPPETS_LINK'."
    exit 1
  fi
fi

# Create the symbolic link. This part is skipped if a directory already existed and contents were copied.
echo "Creating symbolic link from '$SOURCE_SNIPPETS_DIR' to '$DEST_SNIPPETS_LINK'..."
ln -s "$SOURCE_SNIPPETS_DIR" "$DEST_SNIPPETS_LINK"

# Check if the symbolic link creation was successful.
if [ $? -eq 0 ]; then
  echo "Symbolic link created successfully!"
  echo "Obsidian snippets should now be available in your vault."
else
  echo "Error: Failed to create symbolic link."
  exit 1
fi

