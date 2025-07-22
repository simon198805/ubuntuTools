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
elif [ -d "$DEST_SNIPPETS_LINK" ]; then
  echo "Warning: A directory already exists at '$DEST_SNIPPETS_LINK'."
  echo "This script will attempt to replace it with a symbolic link."
  echo "It is recommended to manually move or delete it if you want to preserve its contents."
  read -p "Do you want to proceed and replace it? (y/N): " confirm_replace
  if [[ ! "$confirm_replace" =~ ^[Yy]$ ]]; then
    echo "Aborting. Please handle the existing directory manually."
    exit 0
  fi
  rm -rf "$DEST_SNIPPETS_LINK" # Use -rf to remove directory and its contents
fi

# Create the symbolic link.
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

return 0

