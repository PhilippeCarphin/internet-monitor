#!/usr/bin/env python3

import sys
import datetime

"""
This is the cleanest one.

Code wise, the main thing is that we can simplify a lot by removing the checks
for end of input since the input never ends unless we terminate the program.

Since there is only one condition for breaking, this allows us to avoid the
break that we had in read_outage() in version 2 and replace the single break
with a return statement.
"""

def main():
    for o in generate_outages():
        if o is None:
            return
        d = o['duration']
        print(f"Internet went out at {o['start']} for {d}")

def generate_outages():
    for line in sys.stdin:
        if line is None:
            return
        current_time = get_time(line)
        if "down" in line:
            yield read_outage(sys.stdin, current_time)

def read_outage(file_handle, start_time):
    """
    An outage is in progress, read until we encounter the end
    of the file or until we encounter a line that says the
    internet is working
    """
    for l in file_handle:
        if l is None:
            return
        if "working" in l:
            end_time = get_time(l)
            return {
                "start": start_time,
                "end": end_time,
                "duration" : end_time - start_time
            }

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


try:
    main()
except KeyboardInterrupt:
    pass
