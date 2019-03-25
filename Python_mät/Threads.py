import time as te
import threading
import numpy as np

from acconeer_utils.clients.reg.client import RegClient
from acconeer_utils.clients.json.client import JSONClient
from acconeer_utils.clients import configs
from acconeer_utils import example_utils
from acconeer_utils.mpl_process import PlotProcess, PlotProccessDiedException, FigureUpdater

test = 1


class Radar(threading.Thread):
    def __init__(self):
        # Setup radar data
        self.args = example_utils.ExampleArgumentParser().parse_args()
        example_utils.config_logging(self.args)
        if self.args.socket_addr:
            self.client = JSONClient(self.args.socket_addr)
        else:
            port = self.args.serial_port or example_utils.autodetect_serial_port()
            self.client = RegClient(port)

        self.client.squeeze = False
        self.config = configs.IQServiceConfig()
        self.config.sensor = self.args.sensors
        self.config.range_interval = [0.2, 0.6]
        self.config.sweep_rate = 1
        self.config.gain = 1
        self.time = 5
        self.seq = self.config.sweep_rate * self.time

        self.info = self.client.setup_session(self.config)
        self.num_points = self.info["data_length"]
        self.matrix = np.zeros((self.seq, self.num_points), dtype=np.csingle)
        self.matrix_copy = np.zeros((self.seq, self.num_points), dtype=np.csingle)
        self.matrix_idx = 0
        super(Radar, self).__init__()

    def run(self):
        # Metod för att hämta data från radarn
        self.client.start_streaming()
        for i in range(self.seq*2):
            self.get_data()
            self.tracker()
            self.filter_HeartRate()
            self.filter_RespRate()
            self.matrix_idx += 1
            if self.matrix_idx >= self.seq:
                self.matrix_idx = 0
        self.client.disconnect()

    def get_data(self):
        # Spara fil sker inte senare. Hämtar data från radarn och sparar det i en matris.

        # for i in range(0, self.seq):
        if self.matrix_idx < self.seq:
            self.info, self.data = self.client.get_next()
            self.matrix[self.matrix_idx][:] = self.data[:]
            print("Seq number {}".format(self.matrix_idx))
            te.sleep(1)

        #filename = "test.csv"
        #np.savetxt(filename, self.matrix)

    def filter_HeartRate(self):
        pass

    def filter_RespRate(self):
        pass

    def tracker(self):
        self.matrix_copy = self.matrix
        # matrix_row =
        #tracker_max = np.argmax[np.abs(self.matrix_copy)]

        # print(tracker_max)
        pass


class ExampleFigureUpdater(FigureUpdater):
    def __init__(self, config, num_points):
        self.interval = config.range_interval
        self.num_points = num_points

    def setup(self, fig):
        self.axs = {
            "amplitude": fig.add_subplot(2, 1, 1),
            "phase": fig.add_subplot(2, 1, 2),
        }

        for ax in self.axs.values():
            ax.grid(True)
            ax.set_xlabel("Depth (m)")
            ax.set_xlim(self.interval)

        self.axs["amplitude"].set_title("Amplitude")
        self.axs["amplitude"].set_ylim(0, 0.5)
        self.axs["phase"].set_title("Phase")
        example_utils.mpl_setup_yaxis_for_phase(self.axs["phase"])

        fig.canvas.set_window_title("Acconeer IQ data example")
        fig.set_size_inches(10, 7)
        fig.tight_layout()

    def first(self, d):
        xs = np.linspace(*self.interval, self.num_points)

        self.all_arts = {}
        for key, ax in self.axs.items():
            self.all_arts[key] = [ax.plot(xs, ys)[0] for ys in d[key]]
        return [art for arts in self.all_arts.values() for art in arts]

    def update(self, d):
        for key, arts in self.all_arts.items():
            for art, ys in zip(arts, d[key]):
                art.set_ydata(ys)


def main():

    r = Radar()
    r.start()

    #fig_updater = ExampleFigureUpdater(config, num_points)
    #plot_process = PlotProcess(fig_updater)
    # plot_process.start()

    # plot_data()

    # plot_process.put_data(plot_data)

    # plot_process.close()


if __name__ == "__main__":
    main()
