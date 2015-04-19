from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty
try:
    from jnius import autoclass
    from jnius import cast
    Hardware = autoclass('org.renpy.android.Hardware')
except:
    print "Disable hardware support"
    Hardware = None


__version__ = '0.1'


UDP_IP = "192.168.1.255"
UDP_PORT = 5555
SPORT = None
# TPOWER = 70
# TTURN = 40


class CrazyBotGame(Widget):

    orient1 = NumericProperty(0)
    orient2 = NumericProperty(0)
    m1 = StringProperty("")
    m2 = StringProperty("")
    reverse = NumericProperty(0)
    device = StringProperty("nothing")

    def get_motor_data(self, z, y, r):
        tpower = int(self.ids.powersl.value)
        tturn = int(self.ids.turnsl.value)
        power = int(max(0, min(tpower - float(z), tpower)) * (255.0 / tpower))  # 0  255
        turn = -1 * max(-tturn, min(float(y), tturn)) / float(tturn)  # -1  +1
        m0 = m1 = power
        if turn < 0:
            m1 *= (1 + turn)
        elif turn > 0:
            m0 *= (1 - turn)
        self.m1 = "%d %d" % (int(m1), self.orient1)
        self.m2 = "%d %d" % (int(m0), self.orient2)
        self.device = "%d / %d" % (tpower, tturn)
        return int(m1), int(m0), r

    def send_data(self, data):
        payload = "42,%d,119,%s," % (len(data) + 1, ",".join([str(a) for a in data]))
        if SPORT is not None:
            SPORT.write(payload, 200)
            # self.device = payload

    def update(self, dt):
        if Hardware is not None:
            values = Hardware.orientationSensorReading()
            self.orient1 = int(values[1])
            self.orient2 = int(values[2])
        else:
            self.orient1 = 40
            self.orient2 = 0
        if SPORT is not None:
            # data = [0] * 100
            # num = SPORT.read(data, 100)
            # print num, data
            # self.device = "%d %s" % (num, str(data))
            pass
        v1, v2, r = self.get_motor_data(self.orient2, self.orient1, self.reverse)
        self.send_data([v1, v2, r])


class CrazyBotApp(App):
    def build(self):
        global SPORT
        game = CrazyBotGame()
        if Hardware is not None:
            try:
                import android
                import android.activity  # noqa
                # test for an intent passed to us
                PythonActivity = autoclass('org.renpy.android.PythonActivity')
                UsbManager = autoclass('android.hardware.usb.UsbManager')
                UsbSerialPort = autoclass('com.hoho.android.usbserial.driver.UsbSerialPort')
                Context = autoclass('android.content.Context')
                activity = PythonActivity.mActivity
                intent = activity.getIntent()
                # intent_data = intent.getData()
                device = cast('android.hardware.usb.UsbDevice', intent.getParcelableExtra(UsbManager.EXTRA_DEVICE))
                print device
                Cp21xxSerialDriver = autoclass('com.hoho.android.usbserial.driver.Cp21xxSerialDriver')
                driver = Cp21xxSerialDriver(device)
                print driver
                manager = cast('android.hardware.usb.UsbManager', activity.getSystemService(Context.USB_SERVICE))
                print manager
                port = cast('com.hoho.android.usbserial.driver.UsbSerialPort', driver.getPorts().get(0))
                print port
                connection = cast('android.hardware.usb.UsbDeviceConnection', manager.openDevice(device))
                print connection
                port.open(connection)
                port.setParameters(57600, 8, UsbSerialPort.STOPBITS_1, UsbSerialPort.PARITY_NONE)
                SPORT = port
            except Exception, e:
                print e
                game.device = "E " + str(e)
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
