import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
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

    def get_vels(self, t1=-1, t2=-1):
        dict = self.dict
        ts = sorted(dict.keys())
        vs, ts2 = [], []
        for t in ts:
            d = dict[t]
            vel = d['vel'] if 'vel' in d else vel

            if t1 == -1 or t1 <= t - ts[0] <= t2:
                vs.append(vel)
                ts2.append(t - ts[0])

        return vs, ts2

    def get_3d(self, t1=-1, t2=-1):
        print('extract 3d information ... ')
        dict = self.dict
        ts = sorted(dict.keys())
        xs, ys, zs, vs, modes, ts2 = [], [], [], [], [], []
        mode, alt = 0, 0
        transformer = Transformer.from_crs('epsg:4612', 'epsg:2451')
        for t in ts:
            d = dict[t]
            lat = [d['lat']]
            lon = [d['lon']]
            alt = d['alt'] if 'alt' in d else alt
            vel = d['vel'] if 'vel' in d else vel
            mode = d['mode'] if 'mode' in d else mode

            if t1 == -1 or t1 <= t - ts[0] <= t2:
                y, x = transformer.transform(lat, lon)
                xs.append(x)
                ys.append(y)
                zs.append(alt)
                vs.append(vel)
                modes.append(mode)
                ts2.append(t - ts[0])

        print(f'xs min:{min(xs)} max:{max(xs)} ys min:{min(ys)} ys max:{max(ys)}')
        return xs, ys, zs, vs, modes, ts2


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry('840x725')
        self.create_view(self.root)
        self.nmea = NMEA()

    def create_view(self, root):
        self.f_left = tk.Frame(root, bg='#fdfdf0', relief='groove', bd=3, padx=5, pady=5)
        self.f_right = tk.Frame(root, bg='#fdfdf0', padx=5, pady=5)
        self.f_right_top = tk.Frame(self.f_right, bg='#f8f4e6')
        self.f_right_bottom = tk.Frame(self.f_right, bg='#f8f4e6')
        self.f_map = tk.Frame(self.f_right_top, bg='#f8f4e6', relief='groove', bd=3)
        self.f_vel = tk.Frame(self.f_right_bottom, bg='#f8f4e6', relief='groove', bd=3)
        self.f_3d = tk.Frame(self.f_right_bottom, bg='#f8f4e6', relief='groove', bd=3)

        self.create_control_panel(self.f_left)

        self.f_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        self.f_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.f_right_top.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.f_right_bottom.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.f_map.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.f_vel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.f_3d.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def create_control_panel(self, parent):
        self.button_file = tk.Button(parent, text='Select File', command=self._select_file)
        self.label2 = tk.Label(parent, text='time', bg='#fdfdf0')
        self.textbox1 = tk.Entry(parent, width=10)
        self.textbox2 = tk.Entry(parent, width=10)
        self.button_plot = tk.Button(parent, text='Plot',
                                     command=lambda: [plt.close(), self._map_pitch_plot(), self._plot_vel(),
                                                      self._plot_3d()])

        self.button_file.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5)
        self.label2.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5)
        self.textbox1.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5)
        self.textbox2.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5)
        self.button_plot.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5)

    def run(self):
        self.root.mainloop()

    def _map_pitch_plot(self):
        xs, ys, zs, vs, modes, ts = self.nmea.get_3d()

        fig = plt.figure()
        ax = fig.add_subplot()

        rdedg = gp.read_file('toda/20221001-rdedg.shp')
        wa = gp.read_file('toda/20221001-wa.shp')
        wl = gp.read_file('toda/20221001-wl.shp')
        wstra = gp.read_file('toda/20221001-wstra.shp')
        wstrl = gp.read_file('toda/20221001-wstrl.shp')

        rdedg.plot(ax=ax, color='gray', zorder=4)
        # wa.plot(ax=ax, color='black', zorder=2)
        # wl.plot(ax=ax, color='navy', zorder=1)
        # wstra.plot(ax=ax, color='royalblue', zorder=3)
        # wstrl.plot(ax=ax, color='royalblue', zorder=3)

        ax.scatter(xs, ys, marker='o', s=4, c=vs, cmap='jet', vmin=0.0, vmax=5.0, zorder=5)

        ax.set_xlim(-14650, -14000)
        ax.set_ylim(-22000, -21800)
        canvas = FigureCanvasTkAgg(fig, master=self.f_map)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _plot_vel(self):
        t1 = int(self.textbox1.get())
        t2 = int(self.textbox2.get())
        vs, ts = self.nmea.get_vels(t1, t2)

        fig = plt.figure(figsize=(3.2, 2.4))
        ax = fig.add_subplot()
        ax.plot(ts, vs)
        ax.grid(linestyle=':')
        canvas = FigureCanvasTkAgg(fig, master=self.f_vel)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _plot_3d(self):
        t1 = int(self.textbox1.get())
        t2 = int(self.textbox2.get())
        xs, ys, zs, vs, modes, ts = self.nmea.get_3d(t1, t2)

        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        mappable = ax.scatter(xs, ys, zs, marker='.', c=vs, vmin=0, vmax=5, cmap='jet', zorder=5)

        canvas = FigureCanvasTkAgg(fig, master=self.f_3d)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _select_file(self):
        self.file = tk.filedialog.askopenfilename(initialdir='.', title='Select File')
        if self.file:
            self.root.title('RTKView File: ' + self.file)
            self.nmea.load(self.file)
            self.button_plot.config(stat='active')


def main():
    app = App()
    app.run()


if __name__ == '__main__':
    app = App()
    app.run()