
tmux send-keys "clear" Enter "./pings.sh | tee -a ping_log.txt" Enter
tmux split-window -h -d "tail -f -n +1 ping_log.txt | python3 filter_pings.py --alerts --show-uptimes"
