import os
os.environ['KIVY_NO_FILELOG'] = 'yes'
#os.environ['KIVY_NO_CONSOLELOG'] = 'yes'
import kivy
kivy.require('1.4.0')

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.switch import Switch
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.uix.stacklayout import StackLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.carousel import Carousel
from kivy.gesture import Gesture, GestureDatabase
from kivy.properties import StringProperty, DictProperty
from kivy.clock import Clock
from kivy.factory import Factory
import kivy.core.window

from kivy.support import install_twisted_reactor
install_twisted_reactor()
from twisted.internet import reactor

from ayevent import AyEvent
import datetime
from operator import attrgetter
from functools import partial

class AyObjectApi(BoxLayout):
    v = StringProperty('')
    name = StringProperty('')
    
    def __init__(self, k, apidesc, d, cb):
        #BoxLayout.__init__(self, orientation='horizontal', spacing=10, size_hint_y=None, height=40)
        if k.startswith('api_cmd_'):
            self.name = k[len('api_cmd_'):]
            self.action = True
            self.default = ''
            self.required = False
            self.settable = False
        else:
            self.name = k
            self.action = False
            self.default = apidesc.get('default', 'nil')
            self.required = (apidesc.get('default') == None)
        self.k = k
        self.cb = cb
        self.v = d.get(self.k, '')
        self.apidesc = apidesc
        self.apiformat = self.apidesc.get('apiformat', '')        
        self.f = self.parse_format()

    def load_for_show(self):
        BoxLayout.__init__(self, orientation='horizontal', spacing=10, size_hint_y=None, height=40)

    def on_apply_press(self, btn):
        if self.popupv == None:
            return
        v = []
        if self.f['type'] != 'action':
            pp = [self.f]        
        else:
            pp = self.f['params']
        for ip, p in enumerate(pp):
            if p['type'] == 'combo':
                i = 0
                for w in self.w[ip]:
                    if w.active == True:
                        v.append(p['options'][i])
                        break
                    i += 1
            elif(p['type'] == 'boolean'):
                vv = self.w[ip].active
                if vv == True:
                    v.append('1')
                else:
                    v.append('0')
            elif(p['type'] == 'booleanstring'):
                vv = self.w[ip].active
                if vv == True:
                    v.append('true')
                else:
                    v.append('false')
            else:
                v.append(self.w[ip].text)

        if self.action == False:
            self.cb('set-conf', [self.k, v[0]])
        else:
            self.cb('cmd-action', [self.name, self.f['keys'], v])
            
        self.popupv.dismiss()
        self.popupv = None

    def down_input(self, f):
        if f['type'] == 'combo':
            ww = []            
            w = BoxLayout(orientation='vertical')
            for o in f['options']:
                wb = BoxLayout(orientation='horizontal')
                a = False
                if self.v == o: a = True
                wb.add_widget(Label(text=o))
                wc = CheckBox(group='combo1', active=a)
                wb.add_widget(wc)
                w.add_widget(wb)
                ww.append(wc)
        elif(f['type'] in ['boolean', 'booleanstring']):
            w = Switch(active=(self.v in ['1', 'true']))
            ww = w
        else:
            w = TextInput(text=self.v, multiline=False)
            ww = w
        return w, ww
                
    def down(self):
        print "down", self.f
        popup = Popup(title='Action')
        btn1 = Button(text='Apply')
        btn2 = Button(text='Cancel')
        btn2.bind(on_press=popup.dismiss)
        btn1.bind(on_press=self.on_apply_press)
        ww = []
        self.w = []
        if self.f['type'] != 'action':
            pp = [self.f]        
        else:
            pp = self.f['params']
        for p in pp:
            (w1, w2) = self.down_input(self.f)
            ww.append(w1)
            self.w.append(w2)
                
        self.popupv = popup
        b = BoxLayout(orientation='vertical')
        for w in ww:
            b.add_widget(w)
        b.add_widget(btn1)
        b.add_widget(btn2)
        popup.add_widget(b)
        popup.open()
        
    def parse_format(self):
        if self.apiformat == '': return None
        s = self.apiformat
        if s.find('=') > 0:
            spl = s.split(",")
            ret = spl[0]
            if len(spl) > 1:
                args = spl[1:]
            else:
                args = []
            params = []
            keys = []
            for a in args:
                (k, aa) = a.split('=')
                keys.append(k)
                params.append(self.parse_format_2(aa))
            return {'type': 'action', 'params': params, 'keys': keys}
        if s[0] == '*':
            self.settable = True
            s = s[1:]
        return self.parse_format_2(s)
            
    def parse_format_2(self, s):
        if s.find('(') >= 0:
            ss = s.split('(')[1].split(')')[0]
            f = {'type': 'combo', 'options': [''] + ss.split('|')}
        else:
            f = {'type': s}
        return f

    def mycmp(self, other):
        if other == None: return True
        #required and than name
        if (self.action != other.action):
            return cmp(self.action, other.action)
        if (self.required != other.required):
            return cmp(other.required, self.required)
        return cmp(self.name, other.name)

    def __lt__(self, other):
        return self.mycmp(other) < 0
    def __gt__(self, other):
        return self.mycmp(other) > 0
    def __eq__(self, other):
        return self.mycmp(other) == 0
    def __le__(self, other):
        return self.mycmp(other) <= 0
    def __ge__(self, other):
        return self.mycmp(other) >= 0
    def __ne__(self, other):
        return self.mycmp(other) != 0
        
class AyObject(BoxLayout):

    props = DictProperty({})
    
    def __init__(self, d, cb, supported):
        self.id_ = d['id']
        self.name = d['name']
        self.objtype_ = d['objtype']
        self.supported = supported.params
        self.cb = cb
        self.objapi = []
        self.loaded_for_show = False
        for k,v in self.supported.iteritems():
            if (k.startswith('api_')and(k.startswith('api_cmd')==False)): continue
            o = AyObjectApi(k, v, d, cb)
            self.objapi.append(o)
            self.props[k] = o
        o = AyObjectApi('id', {}, d, cb)
        self.props['id'] = o
        self.objapi.append(o)
        BoxLayout.__init__(self, orientation='vertical', spacing=10, size_hint_y=None, height=40)

    def get_info(self):
        if self.loaded_for_show == False:
            for o in self.objapi:
                o.load_for_show()
            self.loaded_for_show = True
        self.objapi.sort()
        return self.objapi
        
    def __getitem__(self, k):
        return self.props[k]

    def __setitem__(self, k, v):
        o = self.props.get(k)
        if o == None:
            return
        o.v = v
        if k == 'name':
            self.name = v
        self.props[k] = o
        
    def down(self):
        self.cb("object-selected", self)

class AyObjectAylook(AyObject):
    def __init__(self, d, cb, supported):
        AyObject.__init__(self, d, cb, supported)
        
class AyObjectCamera(AyObject):
    def __init__(self, d, cb, supported):
        AyObject.__init__(self, d, cb, supported)

class AyObjectEvent(AyObject):
    def __init__(self, d, cb, supported):
        AyObject.__init__(self, d, cb, supported)

class AyObjectIO(AyObject):
    def __init__(self, d, cb, supported):
        AyObject.__init__(self, d, cb, supported)

class AyObjectVariable(AyObject):
    def __init__(self, d, cb, supported):
        AyObject.__init__(self, d, cb, supported)

class AyObjectPartition(AyObject):
    def __init__(self, d, cb, supported):
        AyObject.__init__(self, d, cb, supported)

class AyObjectZone(AyObject):
    def __init__(self, d, cb, supported):
        AyObject.__init__(self, d, cb, supported)
        
class AyObjectJob(AyObject):
    def __init__(self, d, cb):
        AyObject.__init__(self, d, cb, supported)
        
def object_factory(d, cb, supported):
    if d['objtype'] == 'camera':
        return AyObjectCamera(d, cb, supported)
    elif d['objtype'] == 'aylook':
        return AyObjectAylook(d, cb, supported)
    elif d['objtype'] == 'io':
        return AyObjectIO(d, cb, supported)
    elif d['objtype'] == 'jobs':
        return AyObjectJob(d, cb, supported)
    elif d['objtype'] == 'variable':
        return AyObjectVariable(d, cb, supported)
    elif d['objtype'] == 'event':
        return AyObjectEvent(d, cb, supported)
    elif d['objtype'] == 'partition':
        return AyObjectPartition(d, cb, supported)
    elif d['objtype'] == 'zone':
        return AyObjectZone(d, cb, supported)
    else:
        return AyObject(d, cb, supported)
        
class AyBack(BoxLayout):
    def __init__(self, signal, cb):
        BoxLayout.__init__(self, orientation='horizontal', spacing=10, size_hint_y=None, height=40)
        self.signal = signal
        self.cb = cb
    def down(self):
        self.cb(self.signal, self)

class AyForward(BoxLayout):
    def __init__(self, signal, cb):
        BoxLayout.__init__(self, orientation='horizontal', spacing=10, size_hint_y=None, height=40)
        self.signal = signal
        self.cb = cb
    def down(self):
        self.cb(self.signal, self)

class AyAylook(BoxLayout):
    name = StringProperty('')
    def __init__(self, signal, cb, name, ip, username, password):
        BoxLayout.__init__(self, orientation='horizontal', spacing=10, size_hint_y=None, height=40)
        self.signal = signal
        self.cb = cb
        self.name = name
        self.ip = ip
        self.username = username
        self.password = password
    def down(self):
        self.cb(self.signal, self)
        
class AySupport(BoxLayout):
    def __init__(self, d, cb):
        self.id_ = d['id']
        self.name = d['name']
        self.type_ = d['type']
        self.params = d.get('params', {})
        self.drivers = d.get('drivers', [])
        self.cb = cb
        BoxLayout.__init__(self, orientation='horizontal', spacing=10, size_hint_y=None, height=40)
        if self.name == 'events':
            self.sort = 'eventts'
            self.sort_how = 'desc'
            self.name = 'event'
        else:
            self.sort = 'name'
            self.sort_how = 'asc'            
        self.offset = 0
        self.limit = 20

    def down(self):
        self.cb("supported-selected", self)

class LuAyApp(App):

    def build_config(self, config):
        config.setdefaults('Aylook', {
            'AylookName': '',
            'AylookIp': '',
            'AylookUsername': '',
            'AylookPassword': ''
        })

    def build_settings(self, settings):
        settings.add_json_panel('Aylook', self.config, filename="aysettings.json")

    def handle_ayevent(self, evtype, ev={}):
        #print evtype
        if evtype != 'event': print evtype
        if evtype == 'connected':
            self.ayevent.ask_supported()
        elif evtype == 'disconnected':
            pass
        elif evtype == 'supported':
            self.handle_supported(ev)
        elif evtype == 'supported-selected':
            self.supported_selected = ev
            self.ayevent.ask_objects(ev.type_, ev.sort, ev.sort_how, ev.offset, ev.limit)
        elif evtype == 'objects':
            self.handle_objects(ev, False)
        elif evtype == 'objects-back':
            if self.supported_selected != None:
                self.supported_selected.offset = 0
            self.handle_supported()
        elif evtype == 'object-back':
            self.handle_objects(self.objects, True, False)
        elif evtype == 'objects-next':
            ev = self.supported_selected
            self.ayevent.ask_objects(ev.type_, ev.sort, ev.sort_how, ev.offset, ev.limit)
        elif evtype == 'object-selected':
            self.object_selected = ev
            self.handle_object()
        elif evtype == 'event':
            if ev['name'] == 'OBJECT-CHANGED':
                h = {}
                for p in ev['params']:
                    h[p['key'].lower()] = p['value']
                for o in self.objects:
                    if o.id_ == h['id']:
                        for k,v in h.iteritems():
                            o[k] = v
        elif evtype == 'set-conf':
            self.ayevent.set_conf(self.object_selected.id_, ev[0], ev[1])
        elif evtype == 'cmd-action':
            print "cmd action", ev
            p = {}
            for i,k in enumerate(ev[1]):
                p[k] = ev[2][i]            
            self.ayevent.cmd_action(self.object_selected.id_, ev[0], p)
        elif evtype == 'filter-run':
            print "cmd filter", ev
            self.supported_selected = None
            self.ayevent.ask_objects_filtered(ev)
        elif evtype == 'objects-filtered':
            self.handle_objects(ev, shownext=False)
        elif evtype == 'aylook-selected':
            self.load_aylook(ev)
            self._aylook_btn.state = 'normal'

    def handle_object(self):
        self.clear_list()
        l = self.build_list([AyBack("object-back", self.handle_ayevent)] + self.object_selected.get_info())
        self.layout.add_widget(l)
            
    def handle_objects(self, data, clear=True, factory=True, shownext=True):
        if factory == True:
            added = []
            for d in data:                
                if self.supported_selected == None:
                    for s in self.supported:
                        if d['objtype'] == s.name:
                            ss = s
                else:
                    ss = self.supported_selected                    
                added.append(object_factory(d, self.handle_ayevent, ss))
        else:
            added = data
        if (len(self.objects) == 0)or(clear == True):
            self.objects = []
            self.clear_list()
            sn = []
            if shownext == True:
                sn = [AyForward("objects-next", self.handle_ayevent)]
            l = self.build_list([AyBack("objects-back", self.handle_ayevent)] +added+ sn)
            self.layout.add_widget(l)
        else:
            self.append_list(added, 1)
        self.objects += added
        if self.supported_selected != None:
            self.supported_selected.offset = len(self.objects)
            
    def handle_supported(self, data=None):
        if data != None:
            self.supported = [AySupport(d, self.handle_ayevent) for d in data]
            self.supported.sort(key=attrgetter('name'))
        self.supported_selected = None
        self.objects = []
        self.clear_list()
        l = self.build_list(self.supported)
        self.layout.add_widget(l)

    def clear_list(self):
        self.layout.clear_widgets()
        try:
            self.gridlayout.clear_widgets()
        except:
            pass

    def append_list(self, data, pos=0):
        for l in data:
            self.gridlayout.add_widget(l, pos)        
            
    def build_list(self, data):
        self.gridlayout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.gridlayout.bind(minimum_height=self.gridlayout.setter('height'))
        self.append_list(data)
        root = ScrollView(size_hint=(1, 1))
        root.add_widget(self.gridlayout)
        return root

    def build_loading(self):
        l = Label(text='Loading...')
        return l

    def btn_filter_focus(self, txt, dt):
        txt.focus = True
        
    def btn_filter_state_enter(self, txt):
        t = txt.text
        Clock.schedule_once(partial(self.btn_filter_focus, txt), 0)
        self.handle_ayevent('filter-run', t)

    def btn_filter_state(self, instance, value):
        print "btn", instance, value
        if value == 'down':
            txt = TextInput(multiline=False, focus=True, size_hint=(1, 0.1))
            txt.bind(on_text_validate=self.btn_filter_state_enter)
            self.mainw.add_widget(txt, 0)
        elif value == 'normal':
            self.mainw.remove_widget(self.mainw.children[0])

    def btn_stats_state(self, instance, value):
        print "btn2", instance, value
        if value == 'down':
            gg = self.ayevent.get_all_stats_graph()
            carousel = Carousel(direction='right',  loop=True)
            for g in gg:
                print g
                image = Factory.AsyncImage(source=g, allow_stretch=True)
                carousel.add_widget(image)            
            self._stats_removed = self.mainw.children[0]
            self.mainw.remove_widget(self._stats_removed)
            self.mainw.add_widget(carousel, 0)
        elif value == 'normal':
            self.mainw.remove_widget(self.mainw.children[0])
            self.mainw.add_widget(self._stats_removed)

    def btn_aylook_state(self, instance, value):
        print "btn3", instance, value
        if value == 'down':
            self._aylook_removed = self.mainw.children[0]
            self.mainw.remove_widget(self._aylook_removed)
            self._aylook_btn = instance
            self.ask_aylook()
        elif value == 'normal':
            self.mainw.remove_widget(self.mainw.children[0])
            self.mainw.add_widget(self._aylook_removed)

    #add/remove/modify in luay.ini (/sdcard/.luay.ini on android)
    def ask_aylook(self):
        aaa = self.config.get('Aylook', 'aylooks')
        aa = aaa.split('|')
        aylooks = []
        for a in aa:
            try:
                (name, ip, username, password) = a.split(',')
            except:
                continue
            aylooks.append(AyAylook('aylook-selected', self.handle_ayevent, name, ip, username, password))
        l = self.build_list(aylooks)
        self.mainw.add_widget(l)

    def load_aylook(self, ev):
        self.ayevent = AyEvent(ev.ip, ev.username, ev.password, self.handle_ayevent)
        self.ayevent.connect()
        #self.layout.clear_widgets()
        #self.layout.add_widget(self.build_loading())

    def btn_aylook_click(self, btn, dt):
        btn.state = 'down'        
        
    def build(self):
        self.supported = []
        self.objects = []
        (self.w, self.h) = kivy.core.window.Window.size

        self.mainw = BoxLayout(orientation='vertical', size_hint=(1,1))
        toolbar = BoxLayout(orientation='horizontal', size_hint=(1,0.1))
        toolbar.add_widget(Label(text='LuAy'))
        btn = ToggleButton(text='filter', size_hint=(0.1, 0.8))
        btn.bind(state=self.btn_filter_state)
        toolbar.add_widget(btn)
        btn2 = ToggleButton(text='stats', size_hint=(0.1, 0.8))
        btn2.bind(state=self.btn_stats_state)
        toolbar.add_widget(btn2)
        btn3 = ToggleButton(text='aylook', size_hint=(0.1, 0.8))
        btn3.bind(state=self.btn_aylook_state)
        toolbar.add_widget(btn3)
        self.mainw.add_widget(toolbar)
        self.layout = BoxLayout(orientation='vertical', size_hint=(1, 1))
        self.mainw.add_widget(self.layout)
        Clock.schedule_once(partial(self.btn_aylook_click, btn3), 0)
        return self.mainw
        
if __name__ == '__main__':
    LuAyApp().run()