# Internet Monitor

My internet is dropping for minutes at a time since around Wednesday October
26th 2022.

Since the ISP doesn't monitor this, I decided to do it myself

## Usage

### Simple

Most simple method but no data is saved.

```
./pings.sh | python3 filter_pings.py
```

### Better

```
./pings.sh | python3 filter_pings.sh | tee -a outage_log.txt
```

### Keep raw data

Output the pings to one file
```
./pings.sh >> ping_log.txt
```
and in another shell
```
tail -n +1 -f ping_log.txt | python3 filter_pings.py
```

### Cool

Use `filter_pings_cool.py` instead of `filter_pings.py` to get colored output.



