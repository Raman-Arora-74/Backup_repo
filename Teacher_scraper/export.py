import csv
import os

from pyparsing import line

def append_to_csv(data, filename):

    file_exists = os.path.isfile(filename)
    headers = data[0].keys()

    with open(filename, mode='a+', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        if not file_exists:
            writer.writeheader()

        writer.writerows(data)

def append_url_to_log(url, filename='log.txt'):
    with open(filename, 'a+', encoding='utf-8') as f:
        f.write(url + '\n')        


def read_log_file(filename='log.txt'):
    if not os.path.exists(filename):
        # Create the file if it doesn't exist
        with open(filename, 'w', encoding='utf-8') as f:
            pass  # Just create the file
        return []

    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')  # Explicitly split using "\n"
    
    # Remove any trailing empty lines (optional)
    return lines