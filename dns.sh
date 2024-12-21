#!/usr/bin/env bash

set -o pipefail
dns_check_interval=$((60*60))
while true ; do
    my_ip="$(curl ipinfo.io/ip 2>/dev/null)"
    dns_result="$(nslookup philippe-carphin.ca | tail -n 2 | head -n 1 | awk '{print $2}')"
    if [[ "${dns_result}" == "${my_ip}" ]] ; then
        printf "\033[32m$(date) : dns_result='${dns_result}' matches my_ip\033[0m\n"
    else
        printf "\033[31m$(date) : dns_result='${dns_result}' is different than my_ip='${my_ip}'\033[0m\n"
    fi
    sleep "${dns_check_interval}"
done
