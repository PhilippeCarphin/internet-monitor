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

def main():
    outages = []
    args = get_args()
    with open(args.log_file) as f:
        outage_in_progress = False
        while True:
            l = f.readline().strip()
            if not l:
                if outage_in_progress:
                    outage_end = datetime.datetime.now()
                    outages.append({
                        "start": outage_start,
                        "end": outage_end,
                        "duration": outage_end-outage_start
                    })
                break
            current_time = get_time(l)
            if "down" in l:
                if not outage_in_progress:
                    outage_start = current_time
                    outage_in_progress = True
            elif "working" in l:
                if outage_in_progress:
                    outage_end = current_time
                    outage_in_progress = False
                    outages.append({
                        "start": outage_start,
                        "end": outage_end,
                        "duration": outage_end-outage_start
                    })

    # pprint(outages)
    for o in outages:
        d = o['duration']
        print(f"Internet went out at \033[1;32m{o['start']}\033[0m for \033[1;31m{d}\033[0m")

main()
