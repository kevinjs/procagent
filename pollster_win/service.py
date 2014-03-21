#coding:utf-8
import win32serviceutil
import win32service
import win32event
import win32evtlogutil
import time

class service(win32serviceutil.ServiceFramework):
    _svc_name_ = "test_python"
    _svc_display_name_ = "test_python"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        print 'Service start.'
        
    def SvcDoRun(self):
        import servicemanager
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,servicemanager.PYS_SERVICE_STARTED,(self._svc_name_, ''))

        self.timeout=100
        while True:
            rc=win32event.WaitForSingleObject(self.hWaitStop,self.timeout)
            
            if rc == win32event.WAIT_OBJECT_0:
                break
            else:
                f=open('c:\\time.txt','a')
                f.write('%s %s'%(time.ctime(time.time()), '\n'))
                f.close()
                print 'Service running'
                time.sleep(10)
        return


    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        print 'Service stop'
        return

if __name__=='__main__':
    win32serviceutil.HandleCommandLine(service)
