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

# remove check task from /etc/cron.d
cron_procagent="/etc/cron.d/procagent"

if [ -f "$cron_procagent" ]; then  
    rm ${cron_procagent}

    /etc/init.d/cron restart

    echo "Remove crontab done"
fi

echo "Terminate all"
