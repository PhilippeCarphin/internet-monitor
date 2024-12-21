# Internet Monitor

My internet is dropping for minutes at a time since around Wednesday October
26th 2022.

Since the ISP doesn't monitor this, I decided to do it myself

Here are the [most recent results](https://docs.google.com/spreadsheets/d/e/2PACX-1vRceuyETG0ckgsM54XY-5Wln6jMXlPluvbYKJtV-gjRFVUXxoqStTtVy4UwppC5QTPBKB9x3du5Po8A/pubhtml).

## Usage

Requires Python3 and to generate the excel sheet the pandas and openpyxl packages are needed.

The commands below are for Bash or ZSH so Windows users would need to get that as well.

### Monitoring

- Generate the raw data with `./pings.sh >> pings.txt`
- Filter the raw data with `tail -f -n +1 pings.sh | python3 filter_pings.py --alerts --show-uptimes`

Note: You could also do `./pings.sh | python3 filter_pings.py` but then
you won't have the raw data to pass through the filter to generate the excel
file or if you have to stop the filtering process.

Down times are colored from yellow (short) to red (long) and uptimes are colored
from yellow (short) to green (long).

The alert (if using `--alerts`) rings a bell in the shell which gives you a heads
up that the video you are watching will stop playing once you reach the end of
the buffered part.  It works by printing the "bell" character which depends on
your terminal emulator's configuration.

### Generating the excel sheet

`cat pings.sh | python3 filter_pings_to_excel.py`

will generate a file called `internet_outages.xlsx`

## How it works

The `pings.sh` script runs a `ping -c 1 google.com` every 25 seconds and prints
a line `internet working at <date> (<time>)` if the ping was successful where
`<time>` is the time in ms taken to get a response packet.

If the ping was unsuccessful, another ping is immediately to avoid counting a
single dropped packet as a service interruption.  If the retry ping fails, then
a line `internet down at <date>` is printed.

The Python scripts `filter_pings.py` and `filter_pings_to_excel.py` aggregate
consecutive "UP" lines and consecutive "OUT" lines in the output of `pings.sh`
into intervals of uptime and downtime.


