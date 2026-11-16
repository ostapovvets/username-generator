import random
import re
import csv

#TODO: move the checks into a func tion and put the printing under if __name__ == "__main__":

# cleaning

MIN_ALLOWED = 3
MAX_ALLOWED = 30
ALLOWED_PATTERN = re.compile(r"^[a-zA-Z0-9_.-]+$")

cleaned_names = []
skipped_counts = {
    "empty": 0,
    "too_short": 0,
    "too_long": 0,
    "invalid_char": 0,
}

with open('thematic_usernames.csv', 'r', encoding = 'utf-8') as file:

    for row in csv.DictReader(file):

        name = row["username"].strip().strip("'\"")

        if not name or name.startswith("#"):
            skipped_counts["empty"] += 1
            continue

        if len(name) < MIN_ALLOWED:
            skipped_counts["too_short"] += 1
            continue
        if len(name) > MAX_ALLOWED:
            skipped_counts["too_long"] += 1
            continue
        if not ALLOWED_PATTERN.match(name):
            skipped_counts["invalid_char"] += 1
            continue

        cleaned_names.append(name)

# analysis

if __name__ == "__main__":

    if not cleaned_names:
        print("File's empty or no valid usernames found")
        exit()

    total_count = len(cleaned_names)

    min_length = min(len(name) for name in cleaned_names)
    max_length = max(len(name) for name in cleaned_names)

    shortest = [name for name in cleaned_names if len(name) == min_length]
    longest = [name for name in cleaned_names if len(name) == max_length]
    avg_length = int(sum(len(name) for name in cleaned_names) / total_count)

    all_chars = "".join(cleaned_names)
    unique_chars = sorted(set(all_chars))


    print(total_count, min_length, max_length, avg_length)
    print(shortest)
    print('\n')
    print(longest)
    print(unique_chars)
