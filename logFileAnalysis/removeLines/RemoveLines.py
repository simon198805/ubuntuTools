import os
import re
import sys
import argparse # Import the argparse module

def read_patterns_from_file(pattern_file_path):
    """
    Reads a list of regular expression patterns from a text file, one pattern per line.
    Lines starting with '#' are treated as comments and ignored.

    Args:
        pattern_file_path (str): The path to the file containing the patterns.

    Returns:
        list: A list of strings, where each string is a regex pattern.
    """
    patterns = []
    try:
        with open(pattern_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                stripped_line = line.strip()
                # Ignore empty lines and lines that start with '#' (comments)
                if stripped_line and not stripped_line.startswith('#'):
                    patterns.append(stripped_line)
        return patterns
    except FileNotFoundError:
        print(f"Error: Pattern file not found at '{pattern_file_path}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading pattern file '{pattern_file_path}': {e}")
        sys.exit(1)

def print_help():
    """
    Prints the usage instructions for the script.
    """
    print("Usage: python script_name.py <file_name_pattern> [--pattern <pattern_file_path>] [-d | --debug]")
    print("       python script_name.py [-h | --help]")
    print("\nArguments:")
    print("  <file_name_pattern>  : Regular expression pattern to match log file names.")
    print("                         Example: '.*\\.log\\..*' (matches files like 'my.log.txt', '22_07.log.1')")
    print("\nOptions:")
    print("  --pattern <pattern_file_path> : Path to a text file containing regular expression strings,")
    print("                                  one per line. Lines starting with '#' are ignored as comments.")
    print("                                  If any line within a log block matches any of these patterns,")
    print("                                  the entire block will be removed.")
    print("                                  Defaults to 'logRemovePattern.conf' if not specified.")
    print("  -d, --debug                   : Enable debug mode, which includes a confirmation prompt before processing files.")
    print("  -h, --help                    : Show this help message and exit.")
    print("\nExample:")
    print("  To process all files ending with '.log' using the default 'logRemovePattern.conf':")
    print("    python script_name.py '.*\\.log$'")
    print("\n  To process all files ending with '.log' using a custom pattern file 'my_patterns.txt':")
    print("    python script_name.py '.*\\.log$' --pattern 'my_patterns.txt'")
    print("\n  To process files with a confirmation prompt:")
    print("    python script_name.py '.*\\.log$' -d")
    print("\n  Example 'logRemovePattern.conf' or 'my_patterns.txt' content:")
    print("    # This is a comment, it will be ignored")
    print("    error|warning")
    print("    ^DEBUG.* # Inline comments are not supported, only full line comments")
    print("    Failed to connect")
    print("\nOutput:")
    print("  Modified files will be saved in a 'process/' subdirectory.")
    print("  A summary of processed lines and blocks will be printed to the console.")


def remove_lines_from_files(file_name_pattern, pattern_file_path, debug_mode):
    """
    Removes entire blocks of lines from files matching a given name pattern.
    A block starts with a timestamp (e.g., [HH:MM:SS,ms]) and ends before the next timestamp.
    An entire block is removed if any line within it matches any of the regular expressions
    provided in the pattern file.
    Modified files are saved in a 'process/' subdirectory.

    Args:
        file_name_pattern (str): Regular expression pattern to match file names.
        pattern_file_path (str): Path to a text file containing regular expression strings,
                                 one per line, to match lines within a block that trigger block removal.
        debug_mode (bool): If True, a confirmation prompt will be displayed before processing.
    """
    # Create the 'process' directory if it doesn't exist
    output_dir = "process"
    os.makedirs(output_dir, exist_ok=True)
    print(f"Ensured '{output_dir}/' directory exists.")

    # Read patterns from the provided file
    line_removal_patterns = read_patterns_from_file(pattern_file_path)

    # Print the patterns being used
    print(f"File name pattern provided: '{file_name_pattern}'")
    print(f"Patterns to remove blocks (from file '{pattern_file_path}'):")
    for p in line_removal_patterns:
        print(f"  - '{p}'")

    # Compile regex for file names
    file_regex = re.compile(file_name_pattern)

    # Find files that match the pattern
    matching_files = []
    for filename in os.listdir('.'):
        if os.path.isfile(filename) and file_regex.search(filename):
            matching_files.append(filename)

    if not matching_files:
        print(f"\nNo files found matching the pattern '{file_name_pattern}'. Exiting.")
        sys.exit(0)

    print("\n--- Files to be processed ---")
    for f in matching_files:
        print(f"- {f}")
    
    # Only ask for confirmation if debug_mode is True
    if debug_mode:
        confirm = input(f"\nDo you want to proceed with processing {len(matching_files)} file(s)? (y/n): ").lower()
        if confirm not in ['y', 'yes']:
            print("Processing cancelled by user. Exiting.")
            sys.exit(0)

    # Regex to identify the start of a new log block (e.g., [10:48:42,953])
    timestamp_regex = re.compile(r"^\[\d{2}:\d{2}:\d{2},\d{3}\]")

    # Prepare the line removal regex
    line_removal_regex = None
    if line_removal_patterns:
        # Join all patterns with '|' for an OR condition
        combined_line_removal_pattern = "|".join(f"({p})" for p in line_removal_patterns)
        line_removal_regex = re.compile(combined_line_removal_pattern)
        print(f"Compiled combined line removal regex: '{combined_line_removal_pattern}'")
    else:
        print("No specific line patterns found in the file for block removal. No blocks will be removed based on content.")


    processed_files_count = 0
    skipped_files_count = 0
    total_lines_read = 0
    total_lines_removed = 0
    total_blocks_processed = 0
    total_blocks_removed = 0

    # Iterate through all files in the current directory
    for filename in matching_files: # Iterate only through confirmed matching files
        print(f"\nProcessing file: {filename}")
        input_filepath = filename
        output_filepath = os.path.join(output_dir, filename)
        
        lines_read_in_file = 0
        lines_removed_in_file = 0
        blocks_processed_in_file = 0
        blocks_removed_in_file = 0

        block_buffer = []
        block_contains_match = False

        try:
            with open(input_filepath, 'r', encoding='utf-8') as infile, \
                 open(output_filepath, 'w', encoding='utf-8') as outfile:
                
                for line_num, line in enumerate(infile, 1):
                    lines_read_in_file += 1
                    
                    if timestamp_regex.search(line):
                        # New block started, process the previous block if it exists
                        if block_buffer:
                            blocks_processed_in_file += 1
                            if not block_contains_match:
                                # Write the block if it doesn't contain the pattern
                                for buffered_line in block_buffer:
                                    outfile.write(buffered_line)
                            else:
                                # Discard the block if it contains the pattern
                                lines_removed_in_file += len(block_buffer)
                                blocks_removed_in_file += 1
                        
                        # Start new block
                        block_buffer = [line]
                        block_contains_match = False
                    else:
                        # Continue current block
                        block_buffer.append(line)
                    
                    # Check if the current line (within the current block) matches any of the patterns
                    if line_removal_regex and line_removal_regex.search(line):
                        block_contains_match = True
                
                # Process the last block after the loop finishes
                if block_buffer:
                    blocks_processed_in_file += 1
                    if not block_contains_match:
                        for buffered_line in block_buffer:
                            outfile.write(buffered_line)
                    else:
                        lines_removed_in_file += len(block_buffer)
                        blocks_removed_in_file += 1

            processed_files_count += 1
            total_lines_read += lines_read_in_file
            total_lines_removed += lines_removed_in_file
            total_blocks_processed += blocks_processed_in_file
            total_blocks_removed += blocks_removed_in_file
            print(f"Finished processing '{filename}'. Read {lines_read_in_file} lines, Removed {lines_removed_in_file} lines across {blocks_removed_in_file} blocks. Saved to '{output_filepath}'")

        except Exception as e:
            print(f"Error processing file '{filename}': {e}")
    # Removed the else block for skipped_files_count as we're now filtering upfront
    # and only iterating through matching_files

    print("\n--- Script Summary ---")
    print(f"Total files processed: {processed_files_count}")
    print(f"Total files skipped (name mismatch): {skipped_files_count}") # This will likely be 0 now
    print(f"Total lines read across all processed files: {total_lines_read}")
    print(f"Total lines removed across all processed files: {total_lines_removed}")
    print(f"Total blocks processed across all files: {total_blocks_processed}")
    print(f"Total blocks removed across all files: {total_blocks_removed}")

    # Calculate and print percentages
    percentage_blocks_remained = 0
    if total_blocks_processed > 0:
        blocks_remained = total_blocks_processed - total_blocks_removed
        percentage_blocks_remained = (blocks_remained / total_blocks_processed) * 100
    print(f"Percentage of blocks remained: {percentage_blocks_remained:.2f}%")

    percentage_lines_remained = 0
    if total_lines_read > 0:
        lines_remained = total_lines_read - total_lines_removed
        percentage_lines_remained = (lines_remained / total_lines_read) * 100
    print(f"Percentage of lines remained: {percentage_lines_remained:.2f}%")

    print(f"All modified files are located in the '{output_dir}/' directory.")

if __name__ == "__main__":
    # Check for help argument directly in sys.argv before argparse tries to parse
    if '-h' in sys.argv or '--help' in sys.argv:
        print_help()
        sys.exit(0)

    parser = argparse.ArgumentParser(
        description="Removes log blocks from files based on patterns.",
        add_help=False # We'll handle help manually to use our custom print_help
    )
    parser.add_argument(
        'file_name_pattern',
        type=str,
        help="Regular expression pattern to match log file names."
    )
    parser.add_argument(
        '--pattern',
        type=str,
        default='logRemovePattern.conf', # Default pattern file name
        help="Path to a text file containing regular expression strings (one per line) to match lines within a block that trigger block removal. Defaults to 'logRemovePattern.conf'."
    )
    parser.add_argument(
        '-d', '--debug',
        action='store_true', # This makes it a boolean flag
        help="Enable debug mode, which includes a confirmation prompt before processing files."
    )

    args = parser.parse_args()

    # file_name_pattern is now a required positional argument by default with argparse
    # if it's not present, argparse will automatically raise an error and print usage.
    if args.file_name_pattern is None:
        print("Error: file_name_pattern is required.")
        print_help()
        sys.exit(1)

    file_pattern_arg = args.file_name_pattern
    pattern_file_path_arg = args.pattern
    debug_mode_arg = args.debug # Get the value of the debug flag

    remove_lines_from_files(file_pattern_arg, pattern_file_path_arg, debug_mode_arg)
