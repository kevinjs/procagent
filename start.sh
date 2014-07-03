#!/bin/bash

workspace=$(cd `dirname $0`; pwd)

# check if HttpServer is running
PID_httpsvr=`ps -ef | grep HttpServer.py | grep -v grep | awk '{print $2}'`

if [ -z "$PID_httpsvr" ]
then
    nohup python ${workspace}/HttpServer.py ${workspace} > /tmp/httpsvr.log 2>&1 &
    echo "Start HttpServer done"
fi

sleep 1

# check if PollManager is running
PID_poll=`ps -ef | grep PollManager.py | grep -v grep | awk '{print $2}'`

if [ -z "$PID_poll" ]
then
    python ${workspace}/PollManager.py start
    python ${workspace}/PollManager.py setintvl 6
    python ${workspace}/PollManager.py setpoll "['pollster.cpu.CPUUsagePollster','pollster.mem.MemInfoPollster','pollster.load.LoadStatPollster','pollster.disk.DiskUsagePollster','pollster.net.NetStatPollster','pollster.uptime.UptimePollster']"
    echo "Start Polling task done"
fi

# add start.sh to rc.local
rc_local_file="null"
command="/bin/bash $workspace/start.sh"

if [ -d "/etc/rc.d" ];then
    rc_local_file="/etc/rc.d/rc.local"
else
    rc_local_file="/etc/rc.local"
fi

if [ -f "$rc_local_file" ]; then
    is_exist=`grep -n "$command" $rc_local_file`
    has_exit_0=`grep -n "exit 0" $rc_local_file`

    if [ -z "$is_exist" ]; then
        if [ -z "$has_exit_0" ]; then
            echo $command >> $rc_local_file
        else
            sed -i "/exit 0/ i $command" $rc_local_file
        fi
    fi
else
    cat > $rc_local_file << _done_
#!/bin/sh
$command
exit 0
_done_
    chmod a+x $rc_local_file
    systemctl start rc-local.service
fi

# add check task to /etc/cron.d
cron_procagent="/etc/cron.d/procagent"
cron_path="/usr/sbin/cron"
crond_path="/usr/sbin/crond"

if [ ! -f "$cron_procagent" ]; then  

    cat > ${cron_procagent} << _done_
SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
*/5 * * * * root /bin/bash ${workspace}/start.sh
_done_
    if [ -f "$cron_path" ]; then
        service cron restart
    elif [ -f "$crond_path" ]; then
        service crond restart
    fi

    echo "Add crontab done"
fi

echo "Agent running OK"
