#!/usr/bin/env python3
# pylint: disable=E501

import sys
import datetime
import argparse


def get_arguments():

    p = argparse.ArgumentParser(description="Monitor my god damn internet connection because it seems that stupid Videotron is unable to do it themselves")

    p.add_argument("--show-uptimes", action='store_true')
    p.add_argument("--alerts", action='store_true')
    p.add_argument("--new", action='store_true')
    p.add_argument("--min-working", type=int, default=1)
    p.add_argument("--min-down", type=int, default=1)
    p.add_argument("--count", action='store_true')

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
        "\033[1;38;5;196m",  # red
        "\033[1;38;5;202m",
        "\033[1;38;5;208m",
        "\033[1;38;5;214m",
        "\033[1;38;5;220m",
        "\033[1;38;5;226m",  # yellow
        ]

good_colors = [
        "\033[1;38;5;226m",  # yellow
        "\033[1;38;5;190m",
        "\033[1;38;5;154m",
        "\033[1;38;5;118m",
        "\033[1;38;5;82m",
        "\033[1;38;5;46m",  # Green
]


def main():

    args = get_arguments()

    state = "working"
    old = "working"
    start = sys.stdin.readline()
    interval = {'start': get_time(start)}
    intervals = []
    previous_interval = {}
    current_interval = interval
    nb_working = 0
    nb_down = 0
    for line in sys.stdin:
        # So I can temporarily remove some lines in the test log
        if line.strip().startswith('#'):
            continue
        ltime = get_time(line)
        if args.count:
            if "working" in line:
                nb_working += 1
            elif "down" in line:
                nb_down += 1
            continue
        if args.new:
            #  Keep tabs on how many consecutive "working" or "down" we see
            if "working" in line:
                if nb_working == 0:
                    first_working_time = ltime
                first_down_time = None
                nb_working += 1
                nb_down = 0
            elif "down" in line:
                if nb_down == 0:
                    first_down_time = ltime
                first_working_time = None
                nb_down += 1
                nb_working = 0

            if state == "down":
                # Change state if min_working is surpassed
                # Use >= because args.min_working == 1 should cause a state change
                # when nb_working goes from 0 to 1
                if nb_working >= args.min_working:
                    # STATE CHANGE
                    intervals.append({ "state": "down", "start": current_interval['start'], "end": first_working_time })
                    current_interval = { "state": "working", "start": first_working_time}
                    state = "working"
            if state == "working":
                # Change state if min_down is surpassed
                if nb_down >= args.min_down:
                    intervals.append({ "state": "working", "start": current_interval['start'], "end": first_down_time })
                    current_interval = { "state": "working", "start": first_down_time}
                    state = "down"
        else:
            #
            # Working to working
            #
            if state == "working" and "working" in line:
                print(f"\033[K    \033[1;32mInternet has been working since {interval['start']} for {color_up_duration(ltime - interval['start'])}\033[0m\r", end='')
            #
            # Down to down
            #
            elif state == "down" and "down" in line:
                print(f"\033[K    \033[1;31mInternet has been DOWN since {interval['start']} for {color_out_duration(ltime - interval['start'])}\033[0m\r", end='')
            #
            # Down to working
            #
            elif state == "down" and "working" in line:
                if args.alerts:
                    print("\a", end='')  # Ring bell for state change
                print(f"\033[KInternet went \033[1;31mout\033[0m at \033[1;34m{interval['start'].strftime('%a %Y-%m-%d %H:%M:%S')}\033[0m for {color_out_duration(ltime - interval['start'])}\033[0m")
                interval['start'] = ltime
                state = "working"
                print(f"\033[K    \033[1;32mInternet just went up\033[0m\r", end='')
            #
            # Working to down
            #
            elif state == "working" and "down" in line:
                if args.alerts:
                    print("\a", end='')  # Ring bell for state change
                if args.show_uptimes:
                    print(f"\033[K\033[1mInternet went \033[1;32mup\033[0m  at \033[1;34m{interval['start'].strftime('%a %Y-%m-%d %H:%M:%S')}\033[0m for {color_up_duration(ltime - interval['start'])}\033[0m")
                state = "down"
                interval['start'] = ltime
                print("\033[K    \033[1;31mInternet just went down\033[0m\r", end='')

        # time.sleep(0.01)
    print("")
    if args.count:
        # Because the command is
        # timeout -t 2 ping google.com, and the time sleep between pings is 25s
        # Each consecutive good pings account for 25s each because the time of
        # running the command is negligible.
        # However, for consecutive bad pings, we do two
        # timeout -t 2 ping google.com followed by timeout -t 0.4 ping
        # so for consecutive failures, we have 27.4 seconds
        # So a down ping accounts for 2.4 seconds more than an up ping
        nb_down = (27.4/25) * nb_down
        print(f"nb_down = {nb_down}, nb_working = {nb_working}, down_time_ratio={(nb_down)/(nb_working+(nb_down))}")
    else:
        if args.new:
            up_duration = datetime.timedelta()
            down_duration = datetime.timedelta()
            for i in intervals:
                duration = i['end'] - i['start']
                if i['state'] == "working":
                    up_duration += duration
                else:
                    down_duration += duration
                print_interval(i)
            print(f"len(intervals)={len(intervals)}")
            print(f"Uptime : {up_duration}")
            print(f"down time: {down_duration}")
            print(f"total : {up_duration+down_duration}")
            print((down_duration)/(up_duration+down_duration))
        else:
            print(f"Use --new to get totals")


def print_interval(interval):
    duration = interval['end'] - interval['start']
    if interval['state'] == "working":
        print(f"\033[1mInternet went \033[1;32mup\033[0m  at \033[1;34m{interval['start'].strftime('%a %Y-%m-%d %H:%M:%S')}\033[0m for {color_up_duration(duration)}\033[0m")
    else:
        print(      f"Internet went \033[1;31mout\033[0m at \033[1;34m{interval['start'].strftime('%a %Y-%m-%d %H:%M:%S')}\033[0m for {color_out_duration(duration)}\033[0m")



def transition(old, new, interval, args, ltime):
    if old != new:
        if args.alerts:
            print("\a", end='')  # Ring bell for state change
        print(f"\033[KInternet went \033[1;31mout\033[0m at \033[1;34m{interval['start'].strftime('%a %Y-%m-%d %H:%M:%S')}\033[0m for {color_out_duration(ltime - interval['start'])}\033[0m")
    if old == "working":
        if new == "working":
            print(f"\033[K    \033[1;32mInternet has been working since {interval['start']} for {color_up_duration(ltime - interval['start'])}\033[0m\r", end='')
        elif new == "down":
            if args.show_uptimes:
                print(f"\033[K\033[1mInternet went \033[1;32mup\033[0m  at \033[1;34m{interval['start'].strftime('%a %Y-%m-%d %H:%M:%S')}\033[0m for {color_up_duration(ltime - interval['start'])}\033[0m")
            interval['start'] = ltime
            print("\033[K    \033[1;31mInternet just went down\033[0m\r", end='')
        else:
            pass
    elif old == "down":
        if new == "working":
            print(f"\033[KInternet went \033[1;31mout\033[0m at \033[1;34m{interval['start'].strftime('%a %Y-%m-%d %H:%M:%S')}\033[0m for {color_out_duration(ltime - interval['start'])}\033[0m")
            interval['start'] = ltime
            print(f"\033[K    \033[1;32mInternet just went up\033[0m\r", end='')
        elif new == "down":
            print(f"\033[K    \033[1;32mInternet has been working since {interval['start']} for {color_up_duration(ltime - interval['start'])}\033[0m\r", end='')
        else:
            pass



try:
    main()
except KeyboardInterrupt:
    pass
