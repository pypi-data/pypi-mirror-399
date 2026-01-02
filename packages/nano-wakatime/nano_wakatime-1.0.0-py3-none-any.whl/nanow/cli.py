#!/usr/bin/env python3
"""
Nano WakaTime Wrapper
Author: Alan Nato
License: MIT
Description: A wrapper for GNU Nano that tracks time using the WakaTime CLI.
"""

import sys
import os
import subprocess
import time
import argparse
import shutil
from typing import List

# --- Configuration ---
# Default path for wakatime-cli (standard installation)
WAKATIME_CLI_DEFAULT = os.path.expanduser("~/.wakatime/wakatime-cli")
USER_AGENT = "nano-wakatime/1.0.0"

# Check for watchdog dependency
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("Error: 'watchdog' library is missing.")
    print("Please run: pip3 install -r requirements.txt")
    sys.exit(1)

class WakaTimeHandler(FileSystemEventHandler):
    """
    Handles file system events and triggers the WakaTime CLI.
    """
    def __init__(self, target_files: List[str], cli_path: str):
        self.target_files = [os.path.abspath(f) for f in target_files]
        self.cli_path = cli_path
        self.last_sent = 0
        self.debounce_seconds = 2  # Prevent spamming API on double-saves

    def _send_heartbeat(self, file_path, is_write=False):
        # Rate limiting (Debounce)
        now = time.time()
        if now - self.last_sent < self.debounce_seconds:
            return
        self.last_sent = now

        cmd = [
            self.cli_path,
            "--entity", file_path,
            "--plugin", USER_AGENT
        ]
        
        if is_write:
            cmd.append("--write")

        # Execute quietly in background
        try:
            subprocess.Popen(
                cmd, 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL
            )
        except FileNotFoundError:
            pass # Fail silently to not disrupt user

    def on_modified(self, event):
        if event.is_directory:
            return
        
        # Check if the modified file is one we are editing
        # We use abspath to ensure exact matching
        if os.path.abspath(event.src_path) in self.target_files:
            self._send_heartbeat(os.path.abspath(event.src_path), is_write=True)

def get_target_files(args: List[str]) -> List[str]:
    """
    Filters command line arguments to find valid filenames.
    Ignores flags starting with '-' or '+'.
    """
    files = []
    for arg in args:
        if arg.startswith('-') or arg.startswith('+'):
            continue
        files.append(arg)
    return files

def find_waka_cli():
    """Locates the wakatime-cli binary."""
    if os.path.isfile(WAKATIME_CLI_DEFAULT):
        return WAKATIME_CLI_DEFAULT
    # Fallback to checking PATH
    path_bin = shutil.which("wakatime-cli")
    if path_bin:
        return path_bin
    return None

def main():
    # 1. Parse arguments meant for Nano
    nano_args = sys.argv[1:]
    target_files = get_target_files(nano_args)

    # 2. Locate WakaTime CLI
    cli_path = find_waka_cli()
    if not cli_path:
        # We don't block start, but warn user
        print(f"Warning: WakaTime CLI not found at {WAKATIME_CLI_DEFAULT} or in PATH.")
        time.sleep(1) 

    # 3. Setup the Watcher (if we have files to watch and CLI exists)
    observer = None
    if target_files and cli_path:
        # Create empty files if they don't exist yet (so we can watch them)
        for f in target_files:
            if not os.path.exists(f):
                try:
                    open(f, 'a').close()
                except OSError:
                    pass

        event_handler = WakaTimeHandler(target_files, cli_path)
        observer = Observer()
        
        # Watch the directories of the target files
        watched_dirs = set()
        for f in target_files:
            directory = os.path.dirname(os.path.abspath(f))
            if directory not in watched_dirs:
                if os.path.exists(directory):
                    observer.schedule(event_handler, directory, recursive=False)
                    watched_dirs.add(directory)
        
        observer.start()

    # 4. Start Nano (Blocking Call)
    # We pass all arguments exactly as received to nano
    try:
        subprocess.call(['nano'] + nano_args)

        # Wait 1.5 seconds so we catch the "Save & Exit" event
        if observer:
            time.sleep(1.5)

    except KeyboardInterrupt:
        pass  # Handle Ctrl+C gracefully
    except FileNotFoundError:
        print("Error: 'nano' is not installed or not in your PATH.")
    finally:
        # Now it is safe to kill the watcher
        if observer:
            observer.stop()
            observer.join()

if __name__ == "__main__":
    main()