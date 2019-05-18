import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
# import scipy as sp
from scipy import signal

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
    info = client.setup_session(config)
    num_points = info["data_length"]
    tracking = Tracking(num_points, config.range_interval)

    fig, (amplitude_ax) = plt.subplots(1)
    fig.set_size_inches(12, 6)
    fig.canvas.set_window_title("filename")

    for ax in [amplitude_ax]:
        ax.set_xlabel("time (s)")
        ax.set_xlim(0, num_points/config.sweep_rate)

    amplitude_ax.set_ylabel("Distance (m)")
    amplitude_ax.set_ylim(config.range_interval[0], config.range_interval[1])

    xs = np.linspace(0, num_points/config.sweep_rate, num=num_points)
    amplitude_line = amplitude_ax.plot(xs, np.zeros_like(xs))[0]

    fig.tight_layout()
    plt.ion()
    plt.show()

    interrupt_handler = example_utils.ExampleInterruptHandler()
    print("Press Ctrl-C to end session")

    client.start_streaming()
    counter = 0
    while not interrupt_handler.got_signal:
        info, sweep = client.get_next()
        amplitude = np.abs(sweep)
        track = tracking.tracking(sweep, counter)
        peak = track
        counter += 1
        if counter == num_points:
            counter = 0
        # print(peak)
        amplitude_line.set_ydata(peak)
        # amplitude_line.set_ydata(amplitude)
        fig.canvas.flush_events()

    print("Disconnecting...")
    client.disconnect()


def config_setup():
    config = configs.IQServiceConfig()
    config.range_interval = [0.3, 0.7]
    config.sweep_rate = 100
    config.gain = 1
    #config.session_profile = configs.EnvelopeServiceConfig.MAX_DEPTH_RESOLUTION
    # config.session_profile = configs.EnvelopeServiceConfig.MAX_SNR
    print(config.gain)
    return config
