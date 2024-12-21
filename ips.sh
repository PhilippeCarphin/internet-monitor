#!/usr/bin/env bash

ip_check_interval=3600  # 1 hour
current_ip=$(curl ipinfo.io/ip 2>/dev/null)
echo "starting IP is '${current_ip}'" >&2

while true ; do
    this_ip=$(curl ipinfo.io/ip 2>/dev/null)
    if [[ "${this_ip}" != "${current_ip}" ]] ; then
        echo "Ip has changed from '${current_ip}' to '${this_ip}' on $(date '+%Y-%m-%d %H:%M')"
    fi
    sleep ${ip_check_interval}
done


