procagent
=========

Get system stat info from /proc

Usage:

# Start monitor service
python MonitorManager.py start

# Set the polling interval as 10 sec
python MonitorManager.py setintvl 10

# Set the pollsters list
python MonitorManager.py setpoll "['cpu.CPUInfoPollster','mem.MemStatPollster']"

# Stop monitor service
python MonitorManager.py stop

# Restart monitor service
python MonitorManager.py restart

If you want extend your own pollsters, you can inherite the "PollsterClass" in PollsterClass.py and overload the "getSample" function.


Good luck
dysj4099@gmail.com
