# Log Block Extractor Script

This Python script (`extract_logs.py`) is designed to process log files, extract specific blocks of logs based on patterns defined in a JSON configuration file, and save these blocks into separate, categorized output files. It also provides an option to keep unmatched blocks in separate files, maintaining the original file structure.

## Features

* **Block-based Extraction:** Identifies log blocks based on timestamps (e.g., `[HH:MM:SS,ms]`).

* **Pattern-driven Categorization:** Copies entire log blocks to specific output files if any line within the block matches a defined regular expression pattern.

* **Flexible Configuration:** Uses a JSON file to map output filenames to lists of regex patterns.

* **Optional Block Retention:**

  * **Pattern-level `keep`:** A block matching a pattern with `"keep": true` will be copied to its designated output file AND also remain in the original log's `_unmatched.log` file.

  * **File-level `keep_all_blocks`:** If set to `true` for an given output file, any block copied to that file will *also* be kept in the original log's `_unmatched.log` file, regardless of individual pattern `keep` settings.

* **Unmatched Logs:** Blocks that do not match any patterns (and are not explicitly kept) will be written to a separate `_unmatched.log` file for each original input log file, preserving the original file structure.

* **Sorted Processing:** Processes input log files in alphabetical order.

* **Command-Line Interface:** Easy-to-use command-line arguments for file matching, configuration, and output directory.

* **Help and Sample Config:** Built-in help message and an option to print a sample JSON configuration.

## Installation / Setup

1.  **Save the script:** Save the provided Python code as `extract_logs.py` (or any `.py` filename you prefer).

2.  **Create a configuration file:** Create a JSON file (by default, `splitLog.json`) in the same directory where you will run the script. See the "Configuration File (`splitLog.json`)" section below for its structure.

3.  **Place** your log **files:** Ensure your log files are in the same directory where you run the script, or in a subdirectory that your `log_file_name_pattern` can match.

## Usage

```
python extract_logs.py <log_file_name_pattern> [--config <json_config_file_path>] [--output-dir <directory>]
python extract_logs.py [-h | --help] [-s | --sample-json]
```

### Arguments:

* `<log_file_name_pattern>`: **Required.** A regular expression pattern to match the names of your input log files in the current directory.

    * **Example:** `' .*\.log\..*'` (matches files like `my.log.txt`, `22_07.log.1`)

    * **Example:** `'server_.*\.log$'` (matches files starting with `server_` and ending with `.log`)

### Options:

* `--config <json_config_file_path>`: Path to your JSON configuration file. This file defines the output categories and their matching patterns.

    * **Defaults to:** `splitLog.json` if not specified.

* `--output-dir <directory>`: The directory where all extracted log blocks (both categorized and unmatched) will be saved.

    * **Defaults to:** `processed/`.

* `-s`, `--sample-json`: Prints an example `splitLog.json` configuration to the console and exits.

* `-h`, `--help`: Shows the help message and exits.

### Examples:

1.  **Process all `.log` files using the default `splitLog.json`:**

    ```
    python extract_logs.py '.*\.log$'
    ```

2.  **Process files matching `server_.*\.log` using a custom config file `my_config.json`:**

    ```
    python extract_logs.py 'server_.*\.log' --config 'my_config.json'
    ```

3.  **Process files and save output to a custom directory `my_extracted_logs`:**

    ```
    python extract_logs.py '.*\.log$' --output-dir 'my_extracted_logs'
    ```

4.  **Print the sample JSON configuration:**

    ```
    python extract_logs.py -s
    ```

## Configuration File (`splitLog.json`)

The JSON configuration file defines the mapping between output filenames and the patterns that trigger block extraction.

### Structure:

The root of the JSON is an object where each key is the desired **output filename** (e.g., `"errors.log"`). The value for each output filename is an **object** with the following properties:

* `"patterns"`: **Required.** A list of patterns. Each item in this list can be:

    * A **string**: A regular expression string. If any line in a log block matches this pattern, the block is considered a match for this output file.

    * An **object**: With a `"pattern"` key (string, the regex) and an optional `"keep"` key (boolean).

        * `"keep"`: If `true`, a block matching this specific pattern will be copied to its designated output file AND will *also* be retained in the original log's `_unmatched.log` file. Defaults to `false` if omitted.

* `"keep_all_blocks"`: **Optional.** A boolean. If `true` for a given output file, any block copied to that file will *also* be kept in the original log's `_unmatched.log` file, regardless of individual pattern `keep` settings. Defaults to `false` if omitted.

### Example `splitLog.json`:

```json
{
  "critical_errors.log": {
    "patterns": [
      "CRITICAL ERROR:",
      {
        "pattern": "Fatal exception",
        "keep": true
      },
      "Segmentation fault"
    ],
    "keep_all_blocks": false
  },
  "network_issues.log": {
    "patterns": [
      "Connection refused",
      "Timeout occurred",
      "Network unreachable"
    ]
    // "keep_all_blocks" is omitted here, defaulting to false
  },
  "audit_logs.log": {
    "patterns": [
      "User Login Success",
      "Failed Login Attempt",
      {
        "pattern": "Unauthorized access",
        "keep": true
      }
    ],
    "keep_all_blocks": true
  }
}
```

## Output

The script will create the `--output-dir` (default: `processed/`) if it doesn't exist. Inside this directory, it will create Categorized Log Files, which are files named as specified in your JSON configuration (e.g., `critical_errors.log`, `network_issues.log`). Matching log blocks will be appended to these files.

It will also create Unmatched Log Files. For each input log file (e.g., `server.log`), an `_unmatched.log` file will be created (e.g., `server.log_unmatched.log`). This file will contain: all blocks that did not match any pattern in your configuration; blocks that matched a pattern with `"keep": true`; and blocks that matched a pattern for an output file where `"keep_all_blocks": true`.

A summary of the processing, including the number of files processed, blocks read, and blocks extracted/unmatched, will be printed to the console upon completion.
