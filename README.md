#procagent

A linux monitor agent. Fetch data from procfs.

##Usage:

###1. Start polling task and http server.
	./start.sh

###2. Stop polling task and http server.
	./stop.sh

###3. Get monitor data through http server.
	curl -X GET http://IP_ADDR:8655/getdata
	
###4. Get polling interval through http server.
	curl -X GET http://IP_ADDR:8655/getintvl
	
###5. Get pollsters list through http server.
	curl -X GET http://IP_ADDR:8655/getpollsters

###6. Start polling task through shell
	python PollManager.py start

###7. Stop polling task through shell
	python PollManager.py stop

###8. Restart polling task through shell
	python PollManager.py restart

###9. Set polling interval as 10 sec through shell
	python PollManager.py setintvl 10

###10. Set pollsters
	python PollManager.py setpoll "['pollster.cpu.CPUUsagePollster','pollster.mem.MemInfoPollster']"

####PS. Add pollster in procagent/pollster if you like.

Edit by Kevin Shaw dysj4099@gmail.com
