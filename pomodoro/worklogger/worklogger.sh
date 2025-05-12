#!/bin/bash

# Check if another instance of the script is running
if pgrep -x $(basename "$0") >/dev/null; then
  echo "Another instance of worklogger.sh is already running."
  exit 1
fi

# if command -v gnome-pomodoro>/dev/null ; then
# 	gnome-pomodoro --pause
# fi

start_time=$(date +%s)

WORK_DIR="$HOME/Documents/worklog/"
#WORK_DIR="."
MIN_OT=5	# ask if OT count is OT is more then $MIN_OT min

record_file="$WORK_DIR/$(date +'%m%y')"
cat_file="$WORK_DIR/categories.txt"

# Function to view files
view_file() {
  local file="$1"
  if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$file"
  elif command -v open >/dev/null 2>&1; then # macOS
    open "$file"
  elif command -v nano >/dev/null 2>&1; then
    nano "$file"
  elif command -v vim >/dev/null 2>&1; then
    vim "$file"
  else
    echo "No suitable text editor found. Please view the file manually."
    echo "File: $file"
  fi
}

for i in "$@"; do
  case $i in
    --view)
      view_file "$record_file"
      exit 0
      ;;
    --viewcat)
      view_file "$cat_file"
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
  view_file "$record_file"
  exit
fi

options=()
if [[ -f "$cat_file" ]]; then
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

echo "$(date): Please describe this record (last description >$last_description<, last cat >$last_category<, leave empty will apply last rec):"
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
    if [[ "$category_input" =~ ^[0-9]+$ && "$category_input" -le "${#options[@]}" ]]; then
      category="${options[$((category_input-1))]}"
      break
    elif [[ " ${options[@]} " =~ " $category_input " ]]; then
      category="$category_input"
      break
    else
      read -p "Category '$category_input' does not exist. Would you like to add it? (y/n): " add_category
      if [[ "$add_category" == "y" ]]; then
        options+=("$category_input")
        printf '%s\n' "${options[@]}" > "$cat_file"
        category="$category_input"
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

script_time=$(expr \( $(date +%s) - $start_time \) / 60)
#script_time=5
if [ "$script_time" -ge "$MIN_OT" ]; then
  echo "apply OT $script_time min? (N/y)"
  read OT_opt
  if [ "$OT_opt" == "y" ]; then
    echo "append script time >$script_time< to duration >$duration<"
    duration=$(expr "$duration" + "$script_time" )
  else
    echo "Not taking OT, duration >$duration<"
  fi
fi

rec="$(date +'%Y-%m-%d_%H-%M-%S'):$duration:$category:$description"
echo "new recode >$rec<"
echo "$rec" >> "$record_file"


# if command -v gnome-pomodoro>/dev/null; then
#  echo resume pomodoro
#  gnome-pomodoro --resume
# fi

