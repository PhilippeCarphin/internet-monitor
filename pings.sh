#!/bin/bash
#

# The true time between checks will vary depending on how long the check takes.
# If the internet is working, the time will be close to ${time_between_checks}
# since the ping will take only a few milliseconds.  If the internet is down,
# then the time between checks will be closer to
# $((time_between_checks + ping_timeout))

ping_timeout=2
time_between_checks=25

# Google IP to try if I suspect a DNS problem: 172.217.13.110

set -o pipefail
function internet-works(){
    timeout ${1} bash -c "ping -c 1 google.com | head -n 2 | tail -n 1 | awk '{print \$7}'"
}

function main(){
    local result
    while true ; do

        if result=$(internet-works ${ping_timeout}) ; then
            echo "Internet working at $(date "+%Y-%m-%d %T") (${result})"
        else
            if ! result=$(internet-works 0.4) ; then
                echo "Internet down at $(date "+%Y-%m-%d %T")"
            fi
        fi

        sleep ${time_between_checks}

    done
}

main "$@"
