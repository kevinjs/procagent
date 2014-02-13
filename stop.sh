#!/bin/bash

# Stop polling
python PollManager.py stop
sleep 2

# Stop HttpServer
ps -ef | grep HttpServer.py | grep -v grep | awk '{print $ 2}' | xargs kill

echo "Terminate all"
