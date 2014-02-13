#!/bin/bash

# Start the HttpServer
nohup python HttpServer.py > /tmp/httpsvr.log &
sleep 2

# Start polling
python PollManager.py start
# Set interval of polling as 10 sec
python PollManager.py setintvl 10
# Set pollsters
python PollManager.py setpoll "['pollster.cpu.CPUUsagePollster','pollster.mem.MemInfoPollster','pollster.load.LoadStatPollster']"

echo "Start all"
