from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.properties import NumericProperty
import socket
try:
    from jnius import autoclass
    Hardware = autoclass('org.renpy.android.Hardware')
except:
    print "Disable hardware support"
    Hardware = None


__version__ = '0.1'


UDP_IP = "192.168.1.255"
UDP_PORT = 5555


class CrazyBotGame(Widget):

    orient1 = NumericProperty(0)
    orient2 = NumericProperty(0)
    reverse = NumericProperty(0)

    def send_data(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto("cr,%d,%d,%d" % (self.orient1, self.orient2, self.reverse), (UDP_IP, UDP_PORT))        

    def update(self, dt):
        if Hardware is not None:
            values = Hardware.orientationSensorReading()
            self.orient1 = int(values[1])
            self.orient2 = int(values[2])
        self.send_data()


class CrazyBotApp(App):
    def build(self):
        game = CrazyBotGame()
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game

    def on_stop(self):
        if Hardware is not None:
            Hardware.orientationSensorEnable(False)

    def on_start(self):
        if Hardware is not None:
            Hardware.orientationSensorEnable(True)


if __name__ == '__main__':
    CrazyBotApp().run()
