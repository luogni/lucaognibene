from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.properties import NumericProperty
from jnius import autoclass


__version__ = '0.1'
Hardware = autoclass('org.renpy.android.Hardware')


class CrazyBotGame(Widget):

    orient1 = NumericProperty(0)
    orient2 = NumericProperty(0)

    def update(self, dt):
        print "update"
        values = Hardware.orientationSensorReading()
        print values
        self.orient1 = int(values[1])
        self.orient2 = int(values[2])


class CrazyBotApp(App):
    def build(self):
        game = CrazyBotGame()
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game

    def on_stop(self):
        Hardware.orientationSensorEnable(False)

    def on_start(self):
        Hardware.orientationSensorEnable(True)


if __name__ == '__main__':
    CrazyBotApp().run()
