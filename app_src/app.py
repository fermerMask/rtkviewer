import kivy
kivy.require('2.0.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.scatter import Scatter
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.filechooser import FileChooserListView
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from matplotlib.figure import Figure
from pyproj import Transformer
import geopandas as gp

class NMEA:
    def __init__(self):
        pass

    def load_lines(self, fn):
        lines = open(fn).readlines()
        self.ds = [line.strip().split(',') for line in lines]
        return self.ds

    def load(self, fn):
        lines = open(fn).readlines()
        ds = [line.strip().split(',') for line in lines]

        dict = {}
        for d in ds:
            if d[0] == '$GNGGA' and len(d) == 15 and d[2] != '' and d[4] != '' and d[6] != '':
                t, lat, lon, mode, alt = self.hms_to_sec(d[1]), d[2], d[4], d[6], d[9]
                if t not in dict:
                    dict[t] = {}
                dict[t]['lat'] = self.dm_to_sd(lat)
                dict[t]['lon'] = self.dm_to_sd(lon)
                dict[t]['mode'] = int(mode)
                dict[t]['alt'] = float(alt)

            elif d[0] == '$GNRMC' and len(d) == 14 and d[3] != '' and d[5] != '' and d[7] != '':
                t, lat, lon, vel = self.hms_to_sec(d[1]), d[3], d[5], d[7]
                if t not in dict:
                    dict[t] = {}
                dict[t]['lat'] = self.dm_to_sd(lat)
                dict[t]['lon'] = self.dm_to_sd(lon)
                dict[t]['vel'] = self.mile_to_meter(vel)

        self.dict = dict
        return dict

    def dm_to_sd(self, dm):
        x = float(dm)
        d = x // 100
        m = (x - d * 100) / 60
        return d + m

    def hms_to_sec(self, hms):
        d = [int(c) for c in hms if c != '.']
        h = d[0] * 10 + d[1]
        m = d[2] * 10 + d[3]
        s = d[4] * 10 + d[5] + d[6] * 0.1 + d[7] * 0.01
        t = h * 3600 + m * 60 + s
        return t

    def mile_to_meter(self, mile):
        v = float(mile) * 1.852 * 1000 / 3600
        return v

    def get_vels(self, t1, t2):
        dict = self.dict
        ts = sorted(dict.keys())
        vs, ts2 = [], []
        for t in ts:
            d = dict[t]
            if 'vel' in d:
                vs.append(d['vel'])
                ts2.append(t)
        return ts2, vs

    def get_lats_lons(self, t1, t2):
        dict = self.dict
        ts = sorted(dict.keys())
        lats, lons, ts2 = [], [], []
        for t in ts:
            d = dict[t]
            if 'lat' in d and 'lon' in d:
                lats.append(d['lat'])
                lons.append(d['lon'])
                ts2.append(t)
        return ts2, lats, lons

    def get_3d_data(self, t1, t2):
        dict = self.dict
        ts = sorted(dict.keys())
        lats, lons, alts, ts2 = [], [], [], []
        for t in ts:
            d = dict[t]
            if 'lat' in d and 'lon' in d and 'alt' in d:
                lats.append(d['lat'])
                lons.append(d['lon'])
                alts.append(d['alt'])
                ts2.append(t)
        return ts2, lats, lons, alts


class MainView(BoxLayout):
    def __init__(self, **kwargs):
        super(MainView, self).__init__(**kwargs)
        self.orientation = 'horizontal'

        self.file_chooser = FileChooserListView()
        self.file_chooser.bind(selection=self._on_file_selected)

        self.control_panel = ControlPanel()
        self.control_panel.plot_button.bind(on_press=self._on_plot_button_pressed)

        self.add_widget(self.file_chooser)
        self.add_widget(self.control_panel)

        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)

        self.canvas = FigureCanvasKivyAgg(self.fig)
        self.add_widget(self.canvas)

    def _on_file_selected(self, instance, value):
        if value:
            filename = value[0]
            self.control_panel.filename_label.text = filename

    def _on_plot_button_pressed(self, instance):
        filename = self.control_panel.filename_label.text
        t1 = int(self.control_panel.start_time_input.text)
        t2 = int(self.control_panel.end_time_input.text)

        nmea = NMEA()
        dict = nmea.load(filename)
        ts, lats, lons = nmea.get_lats_lons(t1, t2)

        self.ax.clear()
        self.ax.plot(lons, lats)
        self.canvas.draw()


class ControlPanel(BoxLayout):
    def __init__(self, **kwargs):
        super(ControlPanel, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 10
        self.padding = 10

        self.filename_label = Label(text='No file selected')
        self.add_widget(self.filename_label)

        self.start_time_input = TextInput(hint_text='Start time')
        self.add_widget(self.start_time_input)

        self.end_time_input = TextInput(hint_text='End time')
        self.add_widget(self.end_time_input)

        self.plot_button = Button(text='Plot')
        self.add_widget(self.plot_button)


class NMEAApp(App):
    def build(self):
        return MainView()


if __name__ == '__main__':
    NMEAApp().run()
