#!/usr/bin/env python3

import sys
import datetime
import time
import re
import argparse

def get_arguments():

    p = argparse.ArgumentParser(description="Monitor my god damn internet connection because it seems that stupid Videotron is unable to do it themselves")

    p.add_argument("--show-uptimes", action='store_true')
    p.add_argument("--alerts", action='store_true')

    return p.parse_args()

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


def color_out_duration(d):
    if d < datetime.timedelta(seconds=30):
        color = bad_colors[5]
    elif d < datetime.timedelta(minutes=2):
        color = bad_colors[4]
    elif d < datetime.timedelta(minutes=5):
        color = bad_colors[3]
    elif d < datetime.timedelta(minutes=20):
        color = bad_colors[2]
    elif d < datetime.timedelta(minutes=40):
        color = bad_colors[1]
    else:
        color = bad_colors[0]
    return f"{color}{d}\033[0m"

def color_up_duration(d):
    if d < datetime.timedelta(seconds=30):
        color = bad_colors[4]
    elif d < datetime.timedelta(minutes=1):
        color = good_colors[0]
    elif d < datetime.timedelta(minutes=5):
        color = good_colors[1]
    elif d < datetime.timedelta(minutes=10):
        color = good_colors[2]
    elif d < datetime.timedelta(minutes=40):
        color = good_colors[3]
    elif d < datetime.timedelta(minutes=120):
        color = good_colors[4]
    else:
        color = good_colors[5]
    return f"{color}{d}\033[0m"

bad_colors = [
        "\033[1;38;5;196m", # red
        "\033[1;38;5;202m",
        "\033[1;38;5;208m",
        "\033[1;38;5;214m",
        "\033[1;38;5;220m",
        "\033[1;38;5;226m", # yellow
        ]
good_colors = [
        "\033[1;38;5;226m", # yellow
        "\033[1;38;5;190m",
        "\033[1;38;5;154m",
        "\033[1;38;5;118m",
        "\033[1;38;5;82m",
        "\033[1;38;5;46m", # Green
]

def main():

    args = get_arguments()

    state = "working"
    start = sys.stdin.readline()
    interval = {'start': get_time(start)}
    for l in sys.stdin:
        # So I can temporarily remove some lines in the test log
        if l.strip().startswith('#'):
            continue
        ltime = get_time(l)
        #
        # Working to working
        #
        if state == "working" and "working" in l:
            print(f"\033[K    \033[1;32mInternet has been working since {interval['start']} for {color_up_duration(ltime - interval['start'])}\033[0m\r", end='')
        #
        # Down to down
        #
        elif state == "down" and "down" in l:
            print(f"\033[K    \033[1;31mInternet has been DOWN since {interval['start']} for {color_out_duration(ltime - interval['start'])}\033[0m\r", end='')
        #
        # Down to working
        #
        elif state == "down" and "working" in l:
            if args.alerts:
                print(f"\a", end='') # Ring bell for state change
            print(f"\033[KInternet went \033[1;31mout\033[0m at \033[1;34m{interval['start']}\033[0m for {color_out_duration(ltime - interval['start'])}\033[0m")
            interval = {'start': get_time(l)}
            state = "working"
            print(f"\033[K    \033[1;32mInternet just went up\033[0m\r", end='')
        #
        # Working to down
        #
        elif state == "working" and "down" in l:
            if args.alerts:
                print(f"\a", end='') # Ring bell for state change
            if args.show_uptimes:
                print(f"\033[K\033[1mInternet went \033[1;32mup\033[0m  at \033[1;34m{interval['start']}\033[0m for {color_up_duration(ltime - interval['start'])}\033[0m")
            state = "down"
            interval = {'start': get_time(l)}
            print(f"\033[K    \033[1;31mInternet just went down\033[0m\r", end='')

        # time.sleep(0.01)
    print("")
    return

try:
    main()
except KeyboardInterrupt:
    pass
