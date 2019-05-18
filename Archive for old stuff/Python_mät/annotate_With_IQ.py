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

    config = base_config()
    config.sensor = args.sensors

    info = client.setup_session(config)
    num_points = info["data_length"]

    # Setup plot window for amplitude and phase filled with zeros.
    amplitude_y_max = 1

    fig, (amplitude_ax, phase_ax1) = plt.subplots(2)
    fig.set_size_inches(12, 6)
    fig.canvas.set_window_title("Annotate test")
    fig, (ny_ax2) = plt.subplots(1)
    fig.set_size_inches(8, 5)
    fig.canvas.set_window_title("test två fönster")

    for ax in [amplitude_ax]:
        ax.set_xlabel("Depth (m)")
        ax.set_xlim(config.range_interval)
        ax.grid(True)
    for ax1 in [phase_ax1]:
        ax1.set_xlabel("Depth(m)")
        ax1.set_xlim(config.range_interval)
        ax1.grid(True)

    for ax2 in [ny_ax2]:
        ax2.set_xlabel("Depth (m)")
        ax2.set_xlim(config.range_interval)
        ax2.grid(True)

    amplitude_ax.set_ylabel("Amplitude")
    amplitude_ax.set_ylim(0, 1.0 * amplitude_y_max)
    phase_ax1.set_ylabel("Phase")
    example_utils.mpl_setup_yaxis_for_phase(phase_ax1)

    ny_ax2.set_ylim(-1, 1)

    xs = np.linspace(*config.range_interval, num_points)
    amplitude_line = amplitude_ax.plot(xs, np.zeros_like(xs))[0]
    phase_line = phase_ax1.plot(xs, np.zeros_like(xs))[0]
    ny_line = ny_ax2.plot(xs, np.zeros_like(xs))[0]

    fig.tight_layout()
    plt.ion()
    plt.show()

    # Setup box for annotation with maximum
    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    arrowprops = dict(arrowstyle="->", connectionstyle="angle,angleA=0,angleB=90")
    kw = dict(xycoords='data', textcoords="axes fraction",
              arrowprops=arrowprops, bbox=bbox_props, ha="right", va="top")

    interrupt_handler = example_utils.ExampleInterruptHandler()
    print("Press Ctrl-C to end session")

    client.start_streaming()

    while not interrupt_handler.got_signal:
        # for i in range(0, 1):
        # Get new sensor data
        info, sweep = client.get_next()
        amplitude = np.abs(sweep)
        phase = np.angle(sweep)

        # Update annotation with the new amplitude and position
        ymax = amplitude.max()
        xmax = config.range_interval[0] + (config.range_interval[1] - config.range_interval[0]) * \
            (np.argmax(amplitude)/num_points)
        text = "x={:.2f}, y={:.2f}".format(xmax, ymax)
        annotate = ax.annotate(text, xy=(xmax, ymax), xytext=(0.96, 0.96), **kw)
        vline_ax0 = ax.axvline(x=xmax, ymin=0, ymax=ymax, linewidth=2, color='k')
        vline_ax1 = ax1.axvline(x=xmax, ymin=-np.pi, ymax=np.pi, linewidth=2, color='k')

        # update plot with new sensor data
        amplitude_line.set_ydata(amplitude)
        phase_line.set_ydata(phase)

        if not plt.fignum_exists(1):  # Simple way to check if plot is closed
            break
        fig.canvas.flush_events()
        annotate.remove()
        vline_ax0.remove()
        vline_ax1.remove()

    print("Disconnecting...")
    plt.close()
    client.disconnect()


def base_config():
    config = configs.IQServiceConfig()
    config.range_interval = [0.2, 0.6]
    config.sweep_rate = 1
    config.gain = 0.7
    #config.session_profile = configs.EnvelopeServiceConfig.MAX_SNR
    return config


if __name__ == "__main__":
    main()
