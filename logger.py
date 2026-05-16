import utime
import os

MAX_FILE_SIZE = 50 * 1024  # 50 KB per file
MAX_FILES = 5  # Max 3 files total (150 KB max storage)

def write_log(message):
    current_file = "log1.txt"

    # 1. Check the size of the current log file
    try:
        file_size = os.stat(current_file)[6]  # Index 6 is the size in bytes
    except OSError:
        file_size = 0  # File doesn't exist yet

    # 2. If log1 is too big, rotate the files
    if file_size >= MAX_FILE_SIZE:
        print("Log max size reached. Rotating files...")
        # Delete the oldest file if it exists, shift others down
        for i in range(MAX_FILES, 1, -1):
            old_name = f"log{i - 1}.txt"
            new_name = f"log{i}.txt"
            try:
                os.rename(old_name, new_name)  # Shifts log2->log3, log1->log2
            except OSError:
                pass  # File didn't exist yet

    # 3. Safely append the new message to log1.txt
    with open("log1.txt", "a") as f:
        f.write(message + "\n")