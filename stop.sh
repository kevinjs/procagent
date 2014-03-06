#!/bin/bash

workspace=$(cd `dirname $0`; pwd)

# Stop polling
PID_poll=`ps -ef | grep PollManager.py | grep -v grep | awk '{print $2}'`

if [ -n "$PID_poll" ]
then
    python ${workspace}/PollManager.py stop
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

if [ -f "/tmp/httpsvr.log" ]; then
    rm /tmp/httpsvr.log
fi

if [ -f "/etc/rc.d/rc.local" ]; then
    sed -i "/procagent/d" /etc/rc.d/rc.local
    echo "Remove task from /etc/rc.d/rc.local"
elif [ -f "/etc/rc.local" ]; then
    sed -i "/procagent/d" /etc/rc.local
    echo "Remove task from /etc/rc.local"
fi

echo "Terminate all"
