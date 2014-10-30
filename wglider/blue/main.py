from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.camera import Camera
from kivy.clock import Clock
from kivy.properties import NumericProperty
import plyer
import threading
import datetime
import os.path
from kivy.logger import Logger

__version__ = '0.0.1'


class Blue(Widget):
    lat = NumericProperty(0)
    lon = NumericProperty(0)
    bat = NumericProperty(0)

    def update(self, ):
        pass


class BlueApp(App):
    def build(self):
        self.b = Blue()
        self._lock = threading.Lock()
        Clock.schedule_once(self.update, 5.0)
        return self.b

    def got(self, what):
        self._lock.acquire()
        # Logger.info("blue: got %s" % what)
        self.waiting.remove(what)
        if not self.waiting:
            self._lock.release()
            Clock.schedule_once(self.update, 30.0)
        self._lock.release()

    def got_gps_location(self, **kwargs):
        # Logger.info("GPS: %s" % str(kwargs))
        plyer.gps.stop()
        self.got('gps')

    def got_gps_status(self, message_type, status):
        print "GPS STATUS", message_type, status

    def got_camera_picture(self):
        print "CAMERA2"
        fname = os.path.join(self.user_data_dir, 'picture2.png')
        self.cam.texture.save(fname)
        self.cam.stop()
        self.got('camera')

    def update(self, data):
        print "update", datetime.datetime.now()
        # FIXME: send to server
        # plyer.gps.configure(on_location=self.got_gps_location, on_status=self.got_gps_status)
        # plyer.gps.start()
        print "BATTERY", plyer.battery.status
        self.b.bat = plyer.battery.status['percentage']
        print "CAMERA1"
        self.cam = Camera(on_load=self.got_camera_picture)
        # self.cam.start()
        self.waiting = ['camera']

if __name__ == '__main__':
    BlueApp().run()
