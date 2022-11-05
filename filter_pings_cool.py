#!/usr/bin/env python3

import sys
import datetime
import time
import re

"""
This method so clean that we can unclean it a bit to do some fun printing stuff
that adds an unnecessary else keyword in the read_outage() function.
"""

# TODO When the terminal is not wide enough, my cursor manipulation stuff
# doesn't work correctly.  I need to truncate anything I print that has a
# '\r' in it so that it doesn't go wider than the terminal width.

import os

def print_truncated(string, end='\n'):
    print(string, end=end)
    return
    cr = string.endswith('\r')
    w = os.get_terminal_size().columns
    trunc = string.strip()[:w+1] + '\033[0m\r'
    print(trunc, end=end)

def get_time(log_line):
    """
    Lines are of the form
        Internet working at 2022-10-27 22:08:33
    or
        Internet down at 2022-10-27 22:08:33
    so words 3 and 4 make up the date.
    """
    words = log_line.split()
    time_string = f"{words[3]} {words[4]}"
    dt = datetime.datetime.strptime(time_string, "%Y-%m-%d %H:%M:%S")
    return dt

def read_outage(file_handle, start_time):
    """
    An outage is in progress, read until we encounter the end
    of the file or until we encounter a line that says the
    internet is working
    """
    print("\a========> \033[1;31mINTERNET IS DOWN\033[0m\r", end='')
    for l in file_handle:
        if "working" in l:
            end_time = get_time(l)
            return {
                "start": start_time,
                "end": end_time,
                "duration" : end_time - start_time
            }
        else:
            now = datetime.datetime.now()
            #print(f"========> \033[1;31mINTERNET IS DOWN {now - start_time} and counting\033[0m\r", end = '')
            print_truncated(f"========> \033[1;31mINTERNET IS DOWN {now - start_time} and counting\033[0m\r", end = '')
            # time.sleep(0.01)

def generate_outages():
    for line in sys.stdin:
        current_time = get_time(line)
        if "down" in line:
            yield read_outage(sys.stdin, current_time)

def main():

    for o in generate_outages():
        d = o['duration']
        print(f"\033[KInternet went out at \033[1;34m{o['start']}\033[0m for \033[1;31m{d}\033[0m")
        # Once we receive an outage, that means that the
        # internet is up.  If the internet goes down, this
        # line will be erased.
        print("\a========> \033[1;32mINTERNET IS UP\033[0m\r", end='')

try:
    main()
except KeyboardInterrupt:
    pass
