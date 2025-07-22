import os
import re
import sys
import argparse
import json
from collections import defaultdict

def read_json_config(config_file_path):
    """
    Reads the JSON configuration file containing output filenames and their associated patterns.
    Each output file entry can have an optional "keep_all_blocks" property (boolean), defaulting to false.
    Each pattern can optionally have a "keep" property (boolean), defaulting to false.

    Args:
        config_file_path (str): Path to the JSON configuration file.

    Returns:
        dict: A dictionary where keys are output filenames and values are dictionaries
              containing 'patterns' (list of dicts with 'pattern' (str) and 'keep' (bool))
              and 'keep_all_blocks' (bool).
    """
    try:
        with open(config_file_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        validated_config = {}
        for output_file, output_file_config in config.items():
            if not isinstance(output_file_config, dict):
                raise ValueError(f"Configuration for output file '{output_file}' must be an object.")
            
            if "patterns" not in output_file_config or not isinstance(output_file_config["patterns"], list):
                raise ValueError(f"Output file '{output_file}' must have a 'patterns' key with a list of patterns.")
            
            # keep_all_blocks is optional and defaults to False if not present
            file_keep_all_blocks = output_file_config.get("keep_all_blocks", False)
            if not isinstance(file_keep_all_blocks, bool):
                raise ValueError(f"'keep_all_blocks' property for output file '{output_file}' must be a boolean if specified.")

            validated_patterns = []
            for item in output_file_config["patterns"]:
                pattern_str = None
                pattern_keep_flag = False # Default for pattern-level keep

                if isinstance(item, str):
                    pattern_str = item
                elif isinstance(item, dict):
                    if "pattern" not in item or not isinstance(item["pattern"], str):
                        raise ValueError(f"Pattern definition in '{output_file}' must have a 'pattern' string key.")
                    pattern_str = item["pattern"]
                    # pattern-level keep is optional and defaults to False if not present
                    pattern_keep_flag = item.get("keep", False)
                    if not isinstance(pattern_keep_flag, bool):
                        raise ValueError(f"'keep' property for pattern '{pattern_str}' in '{output_file}' must be a boolean if specified.")
                else:
                    raise ValueError(f"Pattern item in '{output_file}' must be a string or an object with a 'pattern' key.")
                
                validated_patterns.append({"pattern": pattern_str, "keep": pattern_keep_flag})
            
            validated_config[output_file] = {
                "patterns": validated_patterns,
                "keep_all_blocks": file_keep_all_blocks
            }
        return validated_config
    except FileNotFoundError:
        print(f"Error: Configuration file not found at '{config_file_path}'")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in '{config_file_path}': {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error in configuration file '{config_file_path}': {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred while reading config file '{config_file_path}': {e}")
        sys.exit(1)

def print_help():
    """
    Prints the usage instructions for the script.
    """
    print("Usage: python script_name.py <log_file_name_pattern> [--config <json_config_file_path>] [--output-dir <directory>]")
    print("       python script_name.py [-h | --help] [-s | --sample-json]")
    print("\nArguments:")
    print("  <log_file_name_pattern> : Regular expression pattern to match input log file names.")
    print("                            Example: '.*\\.log\\..*' (matches files like 'my.log.txt', '22_07.log.1')")
    print("\nOptions:")
    print("  --config <json_config_file_path> : Path to a JSON configuration file defining which patterns to match")
    print("                                     and which output files to copy matching blocks to.")
    print("                                     Defaults to 'splitLog.json' if not specified.")
    print("  --output-dir <directory> : Directory where the extracted log blocks will be saved.")
    print("                             Defaults to 'processed/'.")
    print("  -s, --sample-json            : Print an example 'splitLog.json' configuration and exit.")
    print("  -h, --help               : Show this help message and exit.")
    print("\nExample JSON Configuration ('splitLog.json' or custom config):")
    print("    {")
    print("      \"errors.log\": {")
    print("        \"patterns\": [")
    print("          \"error\",")
    print("          {\"pattern\": \"fail\", \"keep\": true} # This block will also go to unmatched_blocks.log")
    print("        ],")
    print("        \"keep_all_blocks\": false # Optional, defaults to false")
    print("      },")
    print("      \"debug_info.log\": {")
    print("        \"patterns\": [")
    print("          \"^DEBUG:\",")
    print("          \"INFO: Connected\"")
    print("        ] # 'keep_all_blocks' omitted, defaults to false")
    print("      }")
    print("    }")
    print("\nExample Usage:")
    print("  To extract blocks from all '.log' files using the default 'splitLog.json':")
    print("    python script_name.py '.*\\.log$'")
    print("\n  To extract blocks from all '.log' files using a custom config 'my_config.json':")
    print("    python script_name.py '.*\\.log$' --config 'my_config.json'")
    print("\n  To extract blocks and save them to a custom directory 'my_extracted_logs':")
    print("    python script_name.py '.*\\.log$' --config 'config.json' --output-dir my_extracted_logs")
    print("\n  To print a sample JSON configuration:")
    print("    python script_name.py -s")
    print("\nOutput:")
    print("  Matching log blocks will be appended to the specified output files in the output directory.")
    print("  Blocks not matching any pattern, OR blocks matching a pattern with '\"keep\": true',")
    print("  OR blocks matching a pattern for a destination file with '\"keep_all_blocks\": true',")
    print("  will be appended to a separate file for each original log file,")
    print("  named like 'original_filename_unmatched.log' in the same output directory.")
    print("  A summary of processed files and extracted blocks will be printed to the console.")

def print_sample_json():
    """
    Prints a sample JSON configuration for splitLog.json.
    """
    sample_config = {
        "critical_errors.log": {
            "patterns": [
                "CRITICAL ERROR:",
                {
                    "pattern": "Fatal exception",
                    "keep": True
                },
                "Segmentation fault"
            ],
            "keep_all_blocks": False # Explicitly set to false
        },
        "network_issues.log": {
            "patterns": [
                "Connection refused",
                "Timeout occurred",
                "Network unreachable"
            ]
            # "keep_all_blocks" is omitted here, defaulting to false
        },
        "audit_logs.log": {
            "patterns": [
                "User Login Success",
                "Failed Login Attempt",
                {
                    "pattern": "Unauthorized access",
                    "keep": True
                }
            ],
            "keep_all_blocks": True # Explicitly set to true
        }
    }
    print("\n--- Sample splitLog.json Configuration ---")
    print(json.dumps(sample_config, indent=2))
    print("------------------------------------------")


def extract_log_blocks(log_file_name_pattern, json_config_file_path, output_dir):
    """
    Extracts log blocks matching patterns from specified log files and copies them
    to separate output files based on a JSON configuration. Blocks not matching any
    pattern, or those matching a pattern with "keep": true, or matching a pattern
    for a destination file with "keep_all_blocks": true, are also written to
    a separate unmatched log file for each original log.

    Args:
        log_file_name_pattern (str): Regex pattern for input log files.
        json_config_file_path (str): Path to the JSON config file.
        output_dir (str): Directory to save extracted blocks.
    """
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    print(f"Ensured output directory '{output_dir}/' exists.")

    # Read and compile patterns from the JSON config
    config = read_json_config(json_config_file_path)
    
    if not config:
        print("No patterns defined in the configuration file. All blocks will be considered unmatched.")

    # Compile all regex patterns from the config
    # compiled_patterns = {output_file: {"patterns": [{"regex": compiled_regex, "keep": bool}, ...], "keep_all_blocks": bool}, ...}
    compiled_patterns = {} 
    all_patterns_flat_for_print = [] # For printing
    for output_file, file_config in config.items():
        compiled_patterns[output_file] = {
            "patterns": [],
            "keep_all_blocks": file_config["keep_all_blocks"]
        }
        for pattern_info in file_config["patterns"]:
            pattern_str = pattern_info["pattern"]
            keep_flag = pattern_info["keep"]
            try:
                compiled_patterns[output_file]["patterns"].append({
                    "regex": re.compile(pattern_str),
                    "keep": keep_flag
                })
                all_patterns_flat_for_print.append(f"'{pattern_str}' (keep={keep_flag}) -> '{output_file}' (keep_all_blocks={file_config['keep_all_blocks']})")
            except re.error as e:
                print(f"Error: Invalid regex pattern '{pattern_str}' for output file '{output_file}': {e}")
                sys.exit(1)

    print(f"Input log file pattern: '{log_file_name_pattern}'")
    print(f"Patterns to extract blocks (from '{json_config_file_path}'):")
    if all_patterns_flat_for_print:
        for p_info in all_patterns_flat_for_print:
            print(f"  - {p_info}")
    else:
        print("  (No specific patterns defined, all blocks will go to individual 'unmatched' files)")

    # Compile regex for input log file names
    log_file_regex = re.compile(log_file_name_pattern)

    # Regex to identify the start of a new log block (e.g., [10:48:42,953])
    timestamp_regex = re.compile(r"^\[\d{2}:\d{2}:\d{2},\d{3}\]")

    processed_files_count = 0
    total_blocks_read = 0
    total_blocks_extracted = 0
    total_unmatched_blocks = 0
    
    # Get all files in the current directory and sort them alphabetically
    all_files_in_dir = sorted(os.listdir('.'))
    
    matching_log_files = []
    for filename in all_files_in_dir:
        if os.path.isfile(filename) and log_file_regex.search(filename):
            matching_log_files.append(filename)

    if not matching_log_files:
        print(f"\nNo log files found matching the pattern '{log_file_name_pattern}'. Exiting.")
        sys.exit(0)

    print("\n--- Processing Log Files ---")
    for log_filename in matching_log_files:
        print(f"\nProcessing file: {log_filename}")
        input_filepath = log_filename
        
        # Define the specific unmatched output file for this log_filename
        unmatched_output_file_for_this_log = os.path.join(output_dir, f"{log_filename}_unmatched.log")

        blocks_read_in_file = 0
        blocks_extracted_in_file = 0
        unmatched_blocks_in_file = 0

        block_buffer = []
        # Use a set to store unique output files where the current block should be copied
        block_destination_files = set() 
        block_should_also_keep_unmatched_by_pattern = False # Flag for pattern-level keep
        block_should_also_keep_unmatched_by_file = False # Flag for file-level keep_all_blocks

        try:
            with open(input_filepath, 'r', encoding='utf-8') as infile:
                for line_num, line in enumerate(infile, 1):
                    if timestamp_regex.search(line):
                        # New block started, process the previous block if it exists
                        if block_buffer:
                            blocks_read_in_file += 1
                            if block_destination_files:
                                # Write the block to all identified destination files
                                for dest_file in block_destination_files:
                                    output_filepath = os.path.join(output_dir, dest_file)
                                    with open(output_filepath, 'a', encoding='utf-8') as outfile:
                                        for buffered_line in block_buffer:
                                            outfile.write(buffered_line)
                                blocks_extracted_in_file += 1
                            
                            # Decision for unmatched file:
                            # If no specific pattern matched OR if any matched pattern had "keep": true
                            # OR if any destination file for this block had "keep_all_blocks": true
                            if not block_destination_files or \
                               block_should_also_keep_unmatched_by_pattern or \
                               block_should_also_keep_unmatched_by_file:
                                with open(unmatched_output_file_for_this_log, 'a', encoding='utf-8') as outfile:
                                    for buffered_line in block_buffer:
                                        outfile.write(buffered_line)
                                unmatched_blocks_in_file += 1
                        
                        # Start new block
                        block_buffer = [line]
                        block_destination_files = set() # Reset for the new block
                        block_should_also_keep_unmatched_by_pattern = False # Reset pattern keep flag
                        block_should_also_keep_unmatched_by_file = False # Reset file keep flag
                    else:
                        # Continue current block
                        block_buffer.append(line)
                    
                    # Check if the current line matches any pattern for any output file
                    for output_file, file_config in compiled_patterns.items():
                        for pattern_info in file_config["patterns"]:
                            if pattern_info["regex"].search(line):
                                block_destination_files.add(output_file)
                                if pattern_info["keep"]:
                                    block_should_also_keep_unmatched_by_pattern = True
                                if file_config["keep_all_blocks"]: # Check file-level keep
                                    block_should_also_keep_unmatched_by_file = True
                                # No need to check further patterns for this line if it already matched for this output_file
                                # (Unless we want to ensure all 'keep' flags are considered, which current logic does by not breaking outer loop)
                                # Break from inner loop for patterns for this specific output_file
                                break 
                
                # Process the last block after the loop finishes
                if block_buffer:
                    blocks_read_in_file += 1
                    if block_destination_files:
                        for dest_file in block_destination_files:
                            output_filepath = os.path.join(output_dir, dest_file)
                            with open(output_filepath, 'a', encoding='utf-8') as outfile:
                                for buffered_line in block_buffer:
                                    outfile.write(buffered_line)
                        blocks_extracted_in_file += 1
                    
                    # Decision for unmatched file for the last block:
                    if not block_destination_files or \
                       block_should_also_keep_unmatched_by_pattern or \
                       block_should_also_keep_unmatched_by_file:
                        with open(unmatched_output_file_for_this_log, 'a', encoding='utf-8') as outfile:
                            for buffered_line in block_buffer:
                                outfile.write(buffered_line)
                        unmatched_blocks_in_file += 1

            processed_files_count += 1
            total_blocks_read += blocks_read_in_file
            total_blocks_extracted += blocks_extracted_in_file
            total_unmatched_blocks += unmatched_blocks_in_file
            print(f"Finished processing '{log_filename}'. Read {blocks_read_in_file} blocks, Extracted {blocks_extracted_in_file} blocks, Unmatched {unmatched_blocks_in_file} blocks (to '{os.path.basename(unmatched_output_file_for_this_log)}').")

        except Exception as e:
            print(f"Error processing file '{log_filename}': {e}")

    print("\n--- Script Summary ---")
    print(f"Total log files processed: {processed_files_count}")
    print(f"Total blocks read across all processed files: {total_blocks_read}")
    print(f"Total blocks extracted to specific files: {total_blocks_extracted}")
    print(f"Total blocks written to individual 'unmatched' files: {total_unmatched_blocks}")
    print(f"All extracted blocks are located in the '{output_dir}/' directory.")

if __name__ == "__main__":
    # Check for help or sample-json argument directly in sys.argv before argparse tries to parse
    if '-h' in sys.argv or '--help' in sys.argv:
        print_help()
        sys.exit(0)
    if '-s' in sys.argv or '--sample-json' in sys.argv:
        print_sample_json()
        sys.exit(0)

    parser = argparse.ArgumentParser(
        description="Copies log blocks matching patterns to separate files.",
        add_help=False # We'll handle help manually to use our custom print_help
    )
    parser.add_argument(
        'log_file_name_pattern',
        type=str,
        nargs='?', # Make it optional for when -s is used alone
        help="Regular expression pattern to match input log file names."
    )
    parser.add_argument(
        '--config',
        type=str,
        default='splitLog.json',
        help="Path to a JSON configuration file defining output files and their associated regex patterns. Defaults to 'splitLog.json'."
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='processed',
        help="Directory where the extracted log blocks will be saved. Defaults to 'processed/'."
    )
    parser.add_argument(
        '-s', '--sample-json',
        action='store_true',
        help=argparse.SUPPRESS # Suppress default help for this flag
    )
    # The -h/--help argument is now handled by the direct check above,
    # so we don't need to define it here with argparse.

    args = parser.parse_args()

    # Ensure required positional arguments are provided for normal operation
    if args.log_file_name_pattern is None:
        print("Error: <log_file_name_pattern> is required for normal operation.")
        print_help()
        sys.exit(1)

    extract_log_blocks(
        args.log_file_name_pattern,
        args.config,
        args.output_dir
    )
