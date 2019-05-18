import time as te
import threading
import numpy as np
import queue

from acconeer_utils.clients.reg.client import RegClient
from acconeer_utils.clients.json.client import JSONClient
from acconeer_utils.clients import configs
from acconeer_utils import example_utils
from acconeer_utils.mpl_process import PlotProcess, PlotProccessDiedException, FigureUpdater


class Radar():
    def __init__(self, q):
        # Setup radar
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
        self.config.range_interval = [0.2, 0.6]  # Intervall för mätningar
        self.config.sweep_rate = 10  # Frekvensen
        self.config.gain = 1  # Gain mellan 0 och 1, vi använder 1
        self.time = 5  # Hur lång mätningen ska vara
        # totalt antal sekvenser som krävs för att få en specifik tid
        self.seq = self.config.sweep_rate * self.time

        self.info = self.client.setup_session(self.config)
        self.num_points = self.info["data_length"]  # Antalet mätpunkter per sekvens
        # print(self.num_points)
        # Matris med nollor som fylls med rardardata
        self.matrix = np.zeros((self.seq, self.num_points), dtype=np.csingle)
        self.matrix_copy = np.zeros((self.seq, self.num_points),
                                    dtype=np.csingle)  # En copy på ovanstående
        self.temp_vector = np.zeros((0, self.num_points), dtype=np.csingle)
        self.matrix_idx = 0  # Index för påfyllning av matris
        #super(Radar, self).__init__()
        # En First In First Out (FIFO) kö där mätdata sparas och kan hämtas ut för signalbehandling
        #self.q = q

    def get_data(self):
        # Spara fil sker inte senare. Hämtar data från radarn och sparar det i en matris.

        # for i in range(0, self.seq):
        if self.matrix_idx < self.seq:  # När index är under totala sekvenser fylls matrisen och datan sparas i kön.
            self.info, self.data = self.client.get_next()
            self.temp_vector = np.abs(self.data)

            #self.matrix[self.matrix_idx][:] = self.data[:]
            #print("Seq number {}".format(self.matrix_idx))
            # self.q.put(self.data)
            # print(self.q.get())
        #filename = "test.csv"
        #np.savetxt(filename, self.matrix)

    def filter_HeartRate(self):
        pass

    def filter_RespRate(self):
        pass

    def tracker(self):
        if self.matrix_idx == 0:
            self.amplitude = np.abs(self.data)
            self.peak = np.argmax(self.amplitude)
        else:
            pass
            # print(tracker_max)
        # pass


class ExampleFigureUpdater(FigureUpdater):
    def __init__(self, interval, num_points):
        self.interval = interval
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


class Bluetooth(threading.Thread):
    def __init__(self, qb):
        super(Bluetooth, self).__init__()
        self.qb = qb

    def run(self):
        data = self.qb.get()
        print(data)
        pass


def main():
    # Setup get_data from radar
    q = queue.Queue()
    r = Radar(q)
    # Setup Bluetooth listner
    qb = queue.Queue()

    b = Bluetooth(qb)
    b.start()
    # def run(self):
    # Metod för att hämta data från radarn
    r.client.start_streaming()  # Startar streaming tjänsten (Som ytterligare en egen tråd?)
    # print(r.seq)
    qb.put(100)

    for i in range(r.seq * 2):
        r.get_data()  # Hämta data metoden
        r.tracker()
        r.filter_HeartRate()
        r.filter_RespRate()
        r.matrix_idx += 1
        if r.matrix_idx >= r.seq:
            r.matrix_idx = 0
        print(r.matrix_idx)
        # te.sleep(0.5)
    r.client.disconnect()

    # # Bör vara globala? Så de kan användas både i tråden och här
    # config = [0.2, 0.6]
    # num_points = 827
    # fig_updater = ExampleFigureUpdater(config, num_points)
    # plot_process = PlotProcess(fig_updater)
    # plot_process.start()
    # te.sleep(2)
    # for i in range(0, 10):
    #     data = q.get()
    #     amplitude = np.abs(data)
    #     phase = np.angle(data)
    #     plot_data = {"amplitude": amplitude,
    #                  "phase": phase,
    #                  }
    #     plot_process.put_data(plot_data)
    #     if q.empty() == True:
    #         break
    #     te.sleep(1)

    # plot_process.close()


if __name__ == "__main__":
    main()
