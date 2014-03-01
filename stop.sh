#!/bin/bash

# Stop polling
PID_poll=`ps -ef | grep PollManager.py | grep -v grep | awk '{print $2}'`

if [ -n "$PID_poll" ]
then
    python PollManager.py stop
fi

sleep 1

# Stop HttpServer
ps -ef | grep HttpServer.py | grep -v grep | awk '{print $ 2}' | xargs kill

echo "Terminate all"
