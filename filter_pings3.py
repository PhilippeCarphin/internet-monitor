#!/usr/bin/env python3

import sys
import datetime

def get_time(log_line):
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
    for l in file_handle:
        if "working" in l:
            end_time = get_time(l)
            return {
                "start": start_time,
                "end": end_time,
                "duration" : end_time - start_time
            }

def generate_outages():
    for line in sys.stdin:
        current_time = get_time(line)
        if "down" in line:
            yield read_outage(sys.stdin, current_time)

def main():

    for o in generate_outages():
        d = o['duration']
        print(f"Internet went out at \033[1;32m{o['start']}\033[0m for \033[1;31m{d}\033[0m")


main()
