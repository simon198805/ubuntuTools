# Worklogger

The Worklogger enables you to track your work by recording your work duration, category, and description in a log file. Additionally, you can view the log file and category file.
## Usage

```
worklogger.sh [duration] [--view] [--viewcat] [--closegnome] [--help]
```

### Arguments

- `duration`: the duration of the work in seconds (optional)
- `--view`: opens the log file in a text editor after recording
- `--viewcat`: opens the category file in a text editor
- `--closegnome`: closes the Gnome shell after recording (useful with Pomodoro)
- `--help`: displays the help message

## Working with Pomodoro

To use the Worklog Script with Pomodoro, go to Pomodoro > Preferences > Custom Actions > Add and add the following command:

```
gnome-terminal -- <this script location, can't use $HOME or ~> $(elapsed) --closegnome
```

## How it Works

When you run the script, it prompts you to create a category list if it does not exist yet. After that, you enter a description of your work. If you don't enter a description, the script uses the previous entry's description (if it exists). Then you can either select an existing category or create a new one.

The script then records the timestamp, duration, category, and description in a log file (named after the current month and year). 

If you use the `--view` option, the script opens the log file in a text editor (nano, vim, or vi).
If you use the `--viewcat` option, the script opens the category file in a text editor. If the category file does not exist, the script prompts you to enter categories.

### Record File

The record file is created in the `~/Documents/worklog/` directory and named using the current month and year (e.g., `0423`). Each line in the record file represents a single work activity and has the following format:

```
YYYY-MM-DD_HH-MM-SS:DURATION:CATEGORY:DESCRIPTION
```

### Categories

The `categories.txt` file contains a list of categories that you can use to label work activities. The file is located in the `~/Documents/worklog/` directory. If the file does not exist, the script prompts you to enter categories. You can add new categories by entering them at the prompt. If you enter a category that does not exist in the file, the script prompts you to add it.

## License

This script is released under the MIT License. You can use it, modify it, and distribute it as you see fit.
