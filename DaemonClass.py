#!/usr/bin/env python

import sys, os, time
import atexit

from signal import SIGTERM

import cpu
import mem
import load
import net
import util


def appendFile(content, filename):
    if len(content) != 0:
        output = open(filename, 'a')
        output.write(content)
        output.close()
    else:
        return

def poll():
    cpu_info = cpu.CPUInfo()
    cpu_usage = cpu.CPUUsage()
    mem_info = mem.MemInfo()
    net_info = net.NetStat()
    load_info = load.LoadStat()

    poll_info = {}
    poll_info['cpu_usage'] = cpu_usage
    poll_info['cpu_num'] = len(cpu_info)
    poll_info['mem_free'] = mem_info['MemFree']
    poll_info['mem_total'] = mem_info['MemTotal']
    poll_info['load_1'] = load_info['load_1_min']
    poll_info['load_5'] = load_info['load_5_min']

    poll_info['load_15'] = load_info['load_15_min']
    for net_i in net_info:
        poll_info[net_i+'_recv_bytes'] = net_info[net_i]['Receive']['bytes']
        poll_info[net_i+'_trans_bytes'] = net_info[net_i]['Transmit']['bytes']
        poll_info[net_i+'_recv_pkts'] = net_info[net_i]['Receive']['packets']
        poll_info[net_i+'_trans_pkts'] = net_info[net_i]['Transmit']['packets']
    return poll_info


class Daemon:
    '''
    Usage: subclass the Daemon class and override the run() method
    '''

#    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
#    def __init__(self, pidfile, intvl=10, wait=5, stdin='/dev/stdin', stdout='/dev/stdout', stderr='/dev/stderr'):
    def __init__(self, 
                 pidfile, 
                 stdin='/dev/stdin', 
                 stdout='/dev/stdout', 
                 stderr='/dev/stderr'):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile
#        self.intvl = intvl
#        self.wait = wait
        
    def daemonize(self):
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)
        
        # decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)
        
        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                        # exit from second parent
                        sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)
                
        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())
        
        # write pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())
        file(self.pidfile,'w+').write("%s\n" % pid)
    
    def delpid(self):
        os.remove(self.pidfile)
        
    def start(self):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
        
        if pid:
            message = "pidfile %s already exist. Daemon already running?\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)
        
        # Start the daemon
        self.daemonize()
        self.run()
        
    def stop(self):
        """
        Stop the daemon
        """
        # Get the pid from the pidfile
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
        
        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return # not an error in a restart
        
        # Try killing the daemon process       
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print str(err)
                sys.exit(1)
                
    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self.start()
        
    def run(self):
	c = 0
        while True:
            poll_info = poll()
            content = time.asctime(time.localtime()) + '\n'
            for item in poll_info:
                content += '%s: %s\n' %(item, poll_info[item])
            content += '----------------------------\n\n'
            appendFile(content, '/tmp/testwrite.log')
            time.sleep(10)
            c = c + 1

if __name__ == "__main__":
    daemon = Daemon('/tmp/daemon-example.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print 'Unknown command'
            sys.exit(2)
    else:
        print 'USAGE: %s start/stop/restart' % sys.argv[0]
        sys.exit(2)
            
        
        
