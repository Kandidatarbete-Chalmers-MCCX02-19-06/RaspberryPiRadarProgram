import numpy as np
import matplotlib.pyplot as plt

from acconeer_utils.clients.reg.client import RegClient
from acconeer_utils.clients.json.client import JSONClient
from acconeer_utils.clients import configs
from acconeer_utils import example_utils


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

    amplitude_y_max = 22000

    fig, (amplitude_ax) = plt.subplots(1)
    fig.set_size_inches(12, 6)
    fig.canvas.set_window_title(filename)

    for ax in [amplitude_ax]:
        ax.set_xlabel("Depth (m)")
        ax.set_xlim(config.range_interval)
        ax.set_xticks(np.linspace(0.4, 0.8, num=5))
        ax.set_xticks(np.concatenate([np.linspace(0.41, 0.49, num=9), np.linspace(
            0.51, 0.59, num=9), np.linspace(0.61, 0.69, num=9), np.linspace(0.71, 0.79, num=9)]), minor=True)
        ax.grid(True, which='major')
        ax.grid(True, which='minor')

    amplitude_ax.set_ylabel("Amplitude")
    amplitude_ax.set_ylim(0, 1.1 * amplitude_y_max)

    xs = np.linspace(*config.range_interval, num_points)
    amplitude_line = amplitude_ax.plot(xs, np.zeros_like(xs))[0]

    fig.tight_layout()
    plt.ion()
    plt.show()

    interrupt_handler = example_utils.ExampleInterruptHandler()
    print("Press Ctrl-C to end session")

    client.start_streaming()
    matris = np.zeros((sekvenser, 2))

    while not interrupt_handler.got_signal:
        # for i in range(0, sekvenser):
        info, sweep = client.get_next()
        amplitude = np.abs(sweep)
        ymax = amplitude.max()
        xmax = config.range_interval[0] + (config.range_interval[1] - config.range_interval[0]) * \
            (np.argmax(amplitude)/num_points)
        matris[0][:] = [xmax, ymax]
        matris = np.roll(matris, 1, axis=0)

        text = "x={:.2f}, y={:.2f}".format(xmax, ymax)
        bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
        arrowprops = dict(arrowstyle="->", connectionstyle="angle,angleA=0,angleB=90")
        kw = dict(xycoords='data', textcoords="axes fraction",
                  arrowprops=arrowprops, bbox=bbox_props, ha="right", va="top")
        annotate = ax.annotate(text, xy=(xmax, ymax), xytext=(0.96, 0.96), **kw)

        amplitude_line.set_ydata(amplitude)

        if not plt.fignum_exists(1):  # Simple way to check if plot is closed
            break
        fig.canvas.flush_events()
        annotate.remove()
    # matris = np.mean(matris, axis=0)
    # np.savetxt(filename, matris, delimiter=",")

    print("Disconnecting...")
    plt.close()
    client.disconnect()


def config_setup():
    config = configs.EnvelopeServiceConfig()
    config.range_interval = [0.4, 0.8]
    config.sweep_rate = 2
    config.gain = 1
    return config


if __name__ == "__main__":
    main()
