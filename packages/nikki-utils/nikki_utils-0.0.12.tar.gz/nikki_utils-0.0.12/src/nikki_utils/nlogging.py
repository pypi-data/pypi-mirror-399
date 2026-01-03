#!/usr/bin/env python3
"""
Timestamping utils, including timestamp print with custom logfiles
"""

# built-in
from datetime import datetime
from pathlib import Path

# not exported
DEFAULT_LOG_FILE_PATH = "program.log"
LOG_FILE = None

# exported
DO_LOGGING = True

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

def tsprint(message: str, verbose: bool = True):
    """
    Prints to terminal and logfile with datetime (e.g. "[9/18/2025 15:16:25] message here")
    
    :param message: the message to print
    :type message: str

    :param verbose: whether to output warnings/errors from this function
    :type verbose: bool
    """
    # get datetime and format first, so we can "tsprint" within this function
    now = datetime.now()
    now = now.strftime("%x %X")

    # if we want to log but a log file doesn't exist, create it at the default path
    if DO_LOGGING and not LOG_FILE:
        if verbose: print(f"[{now}] Log file did not exist. Creating at path \"{DEFAULT_LOG_FILE_PATH}\"")
        set_log_file(DEFAULT_LOG_FILE_PATH)

    # do the actual tsprint part
    output = f"[{now}] {message}"
    print(output)

    # if we want to log, try logging.
    if DO_LOGGING:
        try:
            with LOG_FILE.open("a", encoding="utf-8") as file:
                file.write(output + "\n")
        except Exception as e:
            if verbose: print(f"[{now}] Failed to write to log file: {e}")

# tests
if __name__ == "__main__":
    tsprint("program.log test")
    set_log_file("test/dog/cat/log.txt")
    tsprint("log path test")
    DO_LOGGING = False
    tsprint("no logging test")