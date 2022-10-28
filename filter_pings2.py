#!/usr/bin/env python3

import datetime
import argparse
from pprint import pprint

def get_args():
    p = argparse.ArgumentParser(description="Aggregate data from log file from pings.sh")
    p.add_argument("--log-file", help="File with output from pings.sh")

    return p.parse_args()

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
    while True:
        l = file_handle.readline().strip()
        if not l:
            end_time = datetime.datetime.now(),
            break
        if "working" in l:
            end_time = get_time(l)
            break
    return {
        "start": start_time,
        "end": end_time,
        "duration" : end_time - start_time
    }

def main():
    outages = []
    args = get_args()
    with open(args.log_file) as f:
        outage_in_progress = False
        while True:
            l = f.readline().strip()
            if not l:
                break
            current_time = get_time(l)
            if "down" in l:
                outages.append(read_outage(f, current_time))

    # pprint(outages)
    for o in outages:
        d = o['duration']
        print(f"Internet went out at \033[1;32m{o['start']}\033[0m for \033[1;31m{d}\033[0m")

main()
