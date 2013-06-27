import sys
from subprocess import PIPE, Popen
from threading  import Thread
from Queue import Queue, Empty
import sqlite3

##############MAIL#####################
# string "evolution-mail-notification"
# uint32 0
# string "evolution"
# string "New email in Evolution"
# string "Sono stati ricevuti 2 nuovi messaggi."
# array [
#     string "default"
#     string "Mostra In arrivo"
# ]
# array [
#     dict entry(
#         string "urgency"
#         variant             byte 1
#     )
# ]
# int32 -1

#############CHAT########################
# file?

class NotifyMe:
    def __init__(self):
        cmdmonitor = "dbus-monitor --session interface='org.freedesktop.Notifications',member='Notify'"
        p = Popen(cmdmonitor, shell=True, stdout=PIPE, bufsize=1)
        self.q = Queue()
        t = Thread(target=self.enqueue_output, args=(p.stdout, self.q))
        t.daemon = True
        t.start()
        self.sem = sqlite3.connect("/home/luogni/.cache/telepathy/logger/sqlite-data")
        self.empathy_counter = {}
        self.empathy_counter["aylook"] = -1
        self.empathy_counter["imavis"] = -1

    def enqueue_output(self, out, queue):
        for line in iter(out.readline, b''):
            queue.put(line)
        out.close()

    def emit_notification(self, category, msg):
        print "NEW NOTIFICATION", category, msg
        
    def run(self):
        mode = ''
        while True:
            self.check_dbus()
            self.check_empathy("aylook")
            self.check_empathy("imavis")

    def check_empathy(self, channel):
        c = self.sem.cursor()
        c.execute("select messages from messagecounts where identifier='#%s' order by date desc limit 1" % (channel))
        r = c.fetchone()
        cc = int(r[0])
        if (self.empathy_counter[channel] >= 0)and(self.empathy_counter[channel] < cc):
            self.emit_notification("CHAT", "%d new messages on %s" % (cc - self.empathy_counter[channel], channel))
        self.empathy_counter[channel] = cc
            
    def check_dbus(self):
        try:
            line = self.q.get(timeout=.1).strip()
        except Empty:
            pass
        else:
            #got line
            if line.find('New email in Evolution') >= 0:
                self.emit_notification("MAIL", line)
        
if __name__ == '__main__':
    n = NotifyMe()
    n.run()