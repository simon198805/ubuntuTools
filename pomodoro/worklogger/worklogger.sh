#!/bin/bash

if command -v gnome-pomodoro>/dev/null ; then
	gnome-pomodoro --pause
fi

WORK_DIR="$HOME/Documents/worklog/"
record_file=$WORK_DIR/$(date +"%m%y")
cat_file=$WORK_DIR/"categories.txt"
# uset the timpstamp when entering the script
timestamp=$(date +"%Y-%m-%d_%H-%M-%S")

for i in "$@"; do
    case $i in
        --view)
            xdg-open "$record_file"
            exit 0
            ;;
        --viewcat)
            xdg-open "$cat_file"
            exit 0
            ;;
        --closegnome)
            VAR_TERM=true	
            ;;
        --help)
		  echo "Usage: worklogger.sh [duration] [--view] [--viewcat] [--closegnome] [--help]"
		  echo "  duration: the duration of the work in seconds (optional)"
		  echo "  --view: view the worklog file after recording"
		  echo "  --viewcat: view the categories file"
		  echo "  --closegnome: closes the Gnome shell after recording (useful with Pomodoro)"
		  echo "  --help: display this help message"
		  exit 0
            ;;
    esac
done

if [[ "$1" == "--view" ]]; then
    editor=$(command -v nano || command -v vim || command -v vi)
    $editor "$record_file"
    exit
fi

options=()
if [[ -f $cat_file ]]; then
    while read -r line; do
        options+=("$line")
    done < "$cat_file"
else
    echo "Category file does not exist. Please enter the categories."
    while true; do
        read -p "Enter a category (or press Enter to finish): " category
        if [[ -z "$category" ]]; then
            break
        fi
        options+=("$category")
    done
    printf '%s\n' "${options[@]}" > "$cat_file"
fi

    last_record=$(tail -n 1 "$record_file" 2>/dev/null)
    if [[ -n "$last_record" ]]; then
        last_category=$(echo "${last_record}" | cut -d ':' -f 3)
        last_description=$(echo "${last_record}" | cut -d ':' -f 4-)
    else
        last_category=""
        last_description=""
    fi

echo "Please describe this record (last description >$last_description<, last cat >$last_category<, leave empty will apply last rec):"
read description

# if no description, apply last
if [[ -z "$description" ]]; then
	category=$last_category
	description=$last_description
else
# ask for category if there's description input
    for i in "${!options[@]}"; do
        echo "$((i+1)). ${options[i]}"
    done

    while true; do
        read -p "Please select the category by number or name for this input: " category_input
        if [[ $category_input =~ ^[0-9]+$ && $category_input -le ${#options[@]} ]]; then
            category=${options[$((category_input-1))]}
            break
        elif [[ " ${options[@]} " =~ " $category_input " ]]; then
            category=$category_input
            break
        else
            read -p "Category '$category_input' does not exist. Would you like to add it? (y/n): " add_category
            if [[ $add_category == "y" ]]; then
                options+=("$category_input")
                printf '%s\n' "${options[@]}" > "$cat_file"
                category=$category_input
                break
            fi
        fi
    done
fi

if [[ -n "$1" ]]; then
    duration="$(echo "scale=0; $1/60" | bc)"
else
    duration=0
fi

echo "$timestamp:$duration:$category:$description" >> "$record_file"


if command -v gnome-pomodoro>/dev/null
	gnome-pomodoro --resume
fi

if [[ $VAR_TERM == true ]]; then
    # Terminate gnome shell explicitly
    xdotool key Ctrl+Shift+W
fi

