import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

from acconeer_utils.clients.reg.client import RegClient
from acconeer_utils.clients.json.client import JSONClient
from acconeer_utils.clients import configs
from acconeer_utils import example_utils
from acconeer_utils.mpl_process import PlotProcess, PlotProccessDiedException, FigureUpdater


def main():
    args = example_utils.ExampleArgumentParser(num_sens=1).parse_args()
    example_utils.config_logging(args)

    if args.socket_addr:
        client = JSONClient(args.socket_addr)
    else:
        port = args.serial_port or example_utils.autodetect_serial_port()
        client = RegClient(port)

    config = config_setup()
    config.sensor = args.sensors

    tid = 10

    sekvenser = tid * config.sweep_rate
    filename = "Reflektor_2.csv"

    info = client.setup_session(config)
    num_points = info["data_length"]
    fig_updater = FigureUpdater2(config, num_points)
    plot_process = PlotProcess(fig_updater)
    plot_process.start()

    interrupt_handler = example_utils.ExampleInterruptHandler()
    print("Press Ctrl-C to end session")

    client.start_streaming()

    while not interrupt_handler.got_signal:
        info, sweep = client.get_next()
        amplitude = np.abs(sweep)
        plot_data = {
            "amplitude": np.abs(sweep),
            "phase": np.angle(sweep),
            "ymax": amplitude.max(),
            "xmax": config.range_interval[0] + (config.range_interval[1] - config.range_interval[0]) *
            (np.argmax(amplitude)/num_points),
        }
        try:
            plot_process.put_data(plot_data)
        except PlotProccessDiedException:
            break

    print("Disconnecting...")
    plot_process.close()
    client.disconnect()


def config_setup():
    config = configs.EnvelopeServiceConfig()
    config.range_interval = [0.3, 0.7]
    config.sweep_rate = 2
    config.gain = 1
    config.session_profile = configs.EnvelopeServiceConfig.MAX_DEPTH_RESOLUTION
    #config.session_profile = configs.EnvelopeServiceConfig.MAX_SNR
    print(config.gain)
    return config


class FigureUpdater2(FigureUpdater):
    def __init__(self, config, num_points):
        self.config = config
        self.num_points = num_points
        self.plot_index = 0
        #self.xs = np.linspace(*config.range_interval, num_points)

    def setup(self, fig):
        fig.set_size_inches(12, 8)

        gs = GridSpec(1, 1)
        self.amplitude_ax = fig.add_subplot(gs[0, 0])
        self.amplitude_ax.set_xlabel("Depth(m)")
        self.amplitude_ax.set_xlim(*self.config.range_interval)
        self.amplitude_ax.set_ylabel("Amplitude")
        self.amplitude_ax.set_ylim(0, 20000)
        self.amplitude_ax.minorticks_on()
        self.amplitude_ax.grid(True, which='major', color='k')
        self.amplitude_ax.grid(True, which='minor', color='k')

        fig.canvas.set_window_title("Test")
        fig.tight_layout()

    def first(self, data):
        self.process_data(data)
        xmax = 0
        ymax = 0
        text = "x={:.2f}, y={:.2f}".format(data["xmax"], data["ymax"])
        bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
        arrowprops = dict(arrowstyle="->", connectionstyle="angle,angleA=0,angleB=90")
        kw = dict(xycoords='data', textcoords="axes fraction",
                  arrowprops=arrowprops, bbox=bbox_props, ha="right", va="top")

        self.artists = {}

        self.artists["amplitude"] = self.amplitude_ax.plot(self.xs,    data["amplitude"])[0]
        self.artists["annotate"] = self.amplitude_ax.annotate(
            text, xy=(data["xmax"], data["ymax"]), xytext=(0.96, 0.96), **kw)
        return self.artists.values()

    def update(self, data):
        self.process_data(data)
        text = "x={:.2f}, y={:.2f}".format(data["xmax"], data["ymax"])
        bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
        arrowprops = dict(arrowstyle="->", connectionstyle="angle,angleA=0,angleB=90")
        kw = dict(xycoords='data', textcoords="axes fraction",
                  arrowprops=arrowprops, bbox=bbox_props, ha="right", va="top")

        self.artists["annotate"] = self.amplitude_ax.annotate(
            text, xy=(data["xmax"], data["ymax"]), xytext=(0.96, 0.96), **kw)

        self.artists["amplitude"].set_ydata(data["amplitude"])

    def process_data(self, data):
        # if self.plot_index == 0:
        self.xs = np.linspace(*self.config.range_interval, data["amplitude"].size)

        self.plot_index += 1


if __name__ == "__main__":
    main()
