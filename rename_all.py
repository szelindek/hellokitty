#! /usr/bin/python3

import os
import re
import queue

# Init LIFO queue (stack) for depth-first directory traversal 
q = queue.LifoQueue()
# Add current directory as starting point
q.put(os.getcwd())

while not q.empty():
    # List the next directory, pulled from the queue
    path = q.get()
    cwd = os.listdir(path)

    for entry in cwd:
        # Skip renaming hidden files and folders (starting with dot)
        if re.match("^\.", entry):
            continue

        entry_lower = entry.lower()
        entry_path = os.path.join(path,entry)
        entry_lower_path = os.path.join(path,entry_lower)

        # If the entry (file or directory) in the current directory has 
        # uppercase letters in its name, then rename it to all lowercase letters
        if entry != entry_lower:
            try:
                os.rename(entry_path, entry_lower_path)
            except FileNotFoundError:
                print("Couldn't rename: ", entry_path)
        # Add current entry to the queue if it's a directory
        if os.path.isdir(entry_lower_path):
            q.put(entry_lower_path)
