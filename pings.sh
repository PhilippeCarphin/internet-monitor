#!/bin/bash
#

# The true time between checks will vary depending on how long the check takes.
# If the internet is working, the time will be close to ${time_between_checks}
# since the ping will take only a few milliseconds.  If the internet is down,
# then the time between checks will be closer to
# $((time_between_checks + ping_timeout))

ping_timeout=5
time_between_checks=30

function internet-works(){
    timeout ${ping_timeout} ping -c 1 google.com &>/dev/null
}

function main(){
    while true ; do

        if internet-works ; then
            echo "Internet working at $(date "+%Y-%m-%d %T")"
        else
            echo "Internet down at $(date "+%Y-%m-%d %T")"
        fi

        sleep ${time_between_checks}

    done
}

main "$@"
