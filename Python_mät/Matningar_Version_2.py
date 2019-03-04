import numpy as np
import csv
import scipy.io as sp
import time

from acconeer_utils.clients.reg.client import RegClient
from acconeer_utils.clients.json.client import JSONClient
from acconeer_utils.clients import configs
from acconeer_utils import example_utils
from acconeer_utils.mpl_process import PlotProcess, PlotProccessDiedException, FigureUpdater


def main():
    args = example_utils.ExampleArgumentParser().parse_args()
    example_utils.config_logging(args)
    if args.socket_addr:
        client = JSONClient(args.socket_addr)
    else:
        port = args.serial_port or example_utils.autodetect_serial_port()
        client = RegClient(port)

    client.squeeze = False
    # Setup parameters
    config = configs.IQServiceConfig()
    config.sensor = args.sensors
    config.range_interval = [0.20, 0.50]
    config.sweep_rate = 100
    config.gain = 1
    tid = 10
    sekvenser = config.sweep_rate * tid
    config.running_average_factor = 0.5

    info = client.setup_session(config)
    num_points = info["data_length"]
    print(num_points)

    filename = "Ton20_Sweep100_Test6.csv"

    with open("Info_"+filename, "w", newline='\n') as result:
        writer = csv.writer(result, delimiter=';')
        writer.writerow(["Gain: ", str(config.gain)])
        writer.writerow(["Min range:", str(config.range_interval[0])])
        writer.writerow(["Max range:", str(config.range_interval[1])])
        writer.writerow(["Data length:", str(num_points)])
        writer.writerow(["Freq: ", str(config.sweep_rate)])
        writer.writerow(["Tejp: ", "Människa"])
        writer.writerow(["Tid: ", tid])
        writer.writerow(["Sekvenser: ", sekvenser])

    matris = np.zeros((sekvenser, num_points), dtype=np.csingle)
    client.start_streaming()
    print("Starting...")
    start = time.time()
    for i in range(0, sekvenser):
        matris = np.roll(matris, 1, axis=0)
        info, sweep = client.get_next()
        matris[0][:] = sweep[:]
    end = time.time()
    print(i+1)
    print((end - start), "s")
    # print("Disconnecting...")
    np.savetxt(filename, matris, delimiter=";")
    # with open("IQ2_Test.csv", "w", newline='') as f:
    #    writer = csv.writer(f)
    #    writer.writerows(matris)
    #np.savetxt('outfile.csv', matris.view(float), delimiter=";")

    client.disconnect()
    # print(matris)


if __name__ == "__main__":
    main()
