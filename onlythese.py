import argparse
import shutil
import fnmatch
import os
from datetime import datetime
from pathlib import Path

def parse_arguments():
    parser = argparse.ArgumentParser(description="Copy or move files based on patterns and time conditions")
    parser.add_argument('action', choices=['copy', 'move'], help="Action to perform: copy or move")
    parser.add_argument('pattern', help="File pattern to match, e.g., *.txt")
    parser.add_argument('time_type', choices=['created', 'modified'], help="Time type to check: created or modified")
    parser.add_argument('time_condition', choices=['before', 'after'], help="Time condition: before or after")
    parser.add_argument('time_value', help="Time value to compare, format: HH:MM for time or DD/MM/YYYY HH:MM for date and time")
    parser.add_argument('src', help="Source directory")
    parser.add_argument('dest', help="Destination directory")

    return parser.parse_args()

def get_time_from_string(time_str):
    try:
        # Try to parse time only
        return datetime.strptime(time_str, '%H:%M').time()
    except ValueError:
        try:
            # Try to parse date and time
            return datetime.strptime(time_str, '%d/%m/%Y %H:%M')
        except ValueError:
            raise ValueError("Time value must be in format HH:MM or DD/MM/YYYY HH:MM")

def file_time_matches(file_path, time_type, time_condition, comparison_time):
    file_stats = file_path.stat()
    if time_type == 'created':
        file_time = datetime.fromtimestamp(file_stats.st_ctime)
    else:
        file_time = datetime.fromtimestamp(file_stats.st_mtime)

    if isinstance(comparison_time, datetime):
        comparison_time = comparison_time
    else:
        comparison_time = datetime.combine(file_time.date(), comparison_time)

    if time_condition == 'before':
        return file_time < comparison_time
    else:
        return file_time > comparison_time

def main():
    args = parse_arguments()

    comparison_time = get_time_from_string(args.time_value)
    source_path = Path(args.src)
    destination_path = Path(args.dest)

    if not source_path.exists():
        print(f"Source directory '{args.src}' does not exist.")
        return

    if not destination_path.exists():
        print(f"Destination directory '{args.dest}' does not exist.")
        return

    for root, _, files in os.walk(source_path):
        for filename in fnmatch.filter(files, args.pattern):
            file_path = Path(root) / filename
            if file_time_matches(file_path, args.time_type, args.time_condition, comparison_time):
                destination_file_path = destination_path / file_path.relative_to(source_path)
                destination_file_path.parent.mkdir(parents=True, exist_ok=True)  # Create directories if they don't exist
                if args.action == 'copy':
                    shutil.copy(file_path, destination_file_path)
                    print(f"Copied: {file_path} to {destination_file_path}")
                elif args.action == 'move':
                    shutil.move(file_path, destination_file_path)
                    print(f"Moved: {file_path} to {destination_file_path}")

if __name__ == "__main__":
    main()

