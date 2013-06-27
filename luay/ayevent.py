from twisted.internet import reactor, task
from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import ClientCreator
import json
import datetime
import urllib
import md5
import zlib
from kivy.network.urlrequest import UrlRequest

class AyEvent:
    def __init__(self, ip, user, p, cb):
        m = md5.md5()
        m.update('%s:%s' % (user, p))
        if ip.find(':') > 0:
            (self.ip, self.port) = ip.split(':')
            self.port = int(self.port)
        else:
            self.ip = ip
            self.port = 80
        self.user = user
        self.hash_ = m.hexdigest()
        self.cb = cb
        self.rpcurl = 'http://%s:%d/ayapi' % (self.ip, self.port)

    def api2_fail(self, req, error):
        print "API2 RPC FAILED", error

    def api2_ok(self, req, ret):
        #open in gzip format
        print "ret ok"
        ret = json.loads(zlib.decompress(ret, 16+zlib.MAX_WBITS))
        self.events_cb(req._ay_name, ret['data'])

    def set_conf(self, oid, k, v):
        print "set conf"
        self.cmd_action(oid, 'set.conf', {k: v}, 'object-set-conf')

    def cmd_action(self, oid, cmd, params, ay_name='object-cmd-action'):
        params = urllib.urlencode({'method': 'ay_object_action',
                                   'args': json.dumps([self.user, self.hash_, oid, cmd, params])})
        self._req = UrlRequest(self.rpcurl + "?" + params, self.api2_ok, self.api2_fail,
                               req_headers={'Accept-encoding': 'gzip'})
        self._req._ay_name = ay_name
        
    def ask_supported(self):
        params = urllib.urlencode({'method': 'ay_object_get_supported',
                                   'args': json.dumps([self.user, self.hash_, '', ['drivers']])})
        self._req = UrlRequest(self.rpcurl + "?" + params, self.api2_ok, self.api2_fail,
                               req_headers={'Accept-encoding': 'gzip'})
        self._req._ay_name = 'supported'

    def ask_objects(self, t, s, sh, offset, limit):
        print t, s, sh, offset, limit
        params = urllib.urlencode({'method': 'ay_object_list',
                                   'args': json.dumps([self.user, self.hash_, [t], '', '', s, sh, offset, limit])})
        self._req = UrlRequest(self.rpcurl + "?" + params, self.api2_ok, self.api2_fail,
                               req_headers={'Accept-encoding': 'gzip'})
        self._req._ay_name = 'objects'

    def ask_objects_filtered(self, fil):
        params = urllib.urlencode({'method': 'ay_object_list',
                                   'args': json.dumps([self.user, self.hash_, '', '', '', "name", "asc", '', '', fil])})
        print params
        self._req = UrlRequest(self.rpcurl + "?" + params, self.api2_ok, self.api2_fail,
                               req_headers={'Accept-encoding': 'gzip'})
        self._req._ay_name = 'objects-filtered'
        
    def events_cb(self, evtype, ev={}):
        self.cb(evtype, ev)
    
    def connect_events (self):
        c = ClientCreator (reactor, AyEventProtocol, self.ip, self.events_cb, self.user, self.hash_, self.connect_events)
        print datetime.datetime.now(), "Connecting to %s [%s:%s]" % (self.ip, self.user, self.hash_)
        d = c.connectTCP (self.ip, self.port, timeout=10)
        d.addErrback (self.my_error)        

    def my_error (self, tb):
        print "my_error: Connection error.."
        reactor.callLater (5, self.connect_events)        
                
    def connect(self):
        self.connect_events()

    def get_all_stats_graph(self):
        ret = []
        #get list of graph.. add ext=.png because kivy check extension for format..
        for g in [('load', '', 'load'), ('aylook', '', 'uptime'), ('cpu', '0', 'cpu'), ('memory', '', 'memory'), ('aylook', '', 'cpu'), ('aylook', '', 'topmem'), ('aylook', '', 'rss'), ('aylook', '', 'jobwritetime'), ('interface', 'eth0', 'if_octets'), ('aylook', '', 'redisused'), ('aylook', '', 'temp'), ('aylook', '', 'topior'), ('aylook', '', 'topiow'), ('disk', 'md0', 'disk_octets'), ('uptime', '', 'uptime'), ('aylook', '', 'bpstat')]:
            url = "http://%s:%d/stats/graph.php?p=%s&pi=%s&t=%s&h=ay4&s=86400&ext=.png" % (self.ip, self.port, g[0], g[1], g[2])
            ret.append(url)
        return ret            
        
class AyEventProtocol (LineReceiver):
    def __init__ (self, ip, cb, user, h, reconnect):
        self.cb = cb
        self.user = user
        self.hash = h
        self.reconnect = reconnect
        self.shut = False
        self.check_conn = None
        self.ip = ip

    def lose_conn (self):
        try:
            self.transport.loseConnection ()
        except:
            pass

    def shutdown (self):
        self.shut = True            
        self.lose_conn ()
            
    def check_connection(self):
        d1 = datetime.datetime.now ()
        d2 = self.last_event_date
        d = (d1 - d2)
        print d1, "Check connection of %s: %d seconds ago last event" % (self.ip, d.seconds)
        if d.seconds > 80:
            if self.check_conn != None:
                self.check_conn.stop()
                self.check_conn = None
            self.lose_conn()

    def error (self, tb):
        print "error", tb

    def connectionMade (self):
        print datetime.datetime.now(), "Connection made with %s" % self.ip
        self.check_conn = task.LoopingCall(self.check_connection)
        self.last_event_date = datetime.datetime.now ()
        d = self.check_conn.start(30)
        d.addErrback(self.error)
        self.buffer = ''
        msg = 'GET /perl/events.php?user=%s&hash=%s&format=json\r\n' % (urllib.quote(self.user), self.hash)
        print msg
        self.transport.write (msg)
        self.cb('connected')
            
    def connectionLost (self, data):
        print datetime.datetime.now(), "Lost connection with %s" % self.ip
        if self.check_conn != None:
            self.check_conn.stop()
            self.check_conn = None
        if self.shut == False:
            reactor.callLater (5, self.reconnect)
        self.cb('disconnected')
            
    def lineReceived (self, data):
        self.buffer += data
        try:
            ev = json.loads(self.buffer)
        except:
            ev = None
        if ev != None:
            self.last_event_date = datetime.datetime.now()
            self.cb ('event', ev)
            self.buffer = ''

