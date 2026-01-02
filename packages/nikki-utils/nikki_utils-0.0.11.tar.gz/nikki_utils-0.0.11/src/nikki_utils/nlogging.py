#!/usr/bin/env python3
"""
Timestamping utils, including timestamp print with custom logfiles
"""

# built-in
from datetime import datetime
from pathlib import Path

LOG_FILE = None

def set_log_file(log_file_path: str):
    """
    Sets the log file path (relative or absolute), creating the directories and files as necessary.
    
    :param log_file_path: The new log file path to update to.
    :type log_file_path: str
    """
    global LOG_FILE
    LOG_FILE = Path(log_file_path)

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True) # mkdirs above the file
    LOG_FILE.touch(exist_ok=True) # create the file if it doesn't exist

def tsprint(message: str, log: bool = True):
    """
    Prints to terminal and logfile with datetime (e.g. "[9/18/2025 15:16:25] message here")

    Args:
    :param message: the message to print
    :type message: str
    :param log: whether to log to the log file. off by default
    :type log: bool
    """

    if not LOG_FILE:
        set_log_file("program.log")

    now = datetime.now()
    now = now.strftime("%x %X")
    output = f"[{now}] {message}"
    print(output)

    if log:
        try:
            with LOG_FILE.open("a", encoding="utf-8") as file:
                file.write(output + "\n")
        except Exception as e:
            print(f"[{now}] Failed to write to log file: {e}")

# tests
if __name__ == "__main__":
    tsprint("test 1")
    set_log_file("test/dog/cat/log.txt")
    tsprint("test 2")