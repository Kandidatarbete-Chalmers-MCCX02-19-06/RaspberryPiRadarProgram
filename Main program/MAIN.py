import time
import threading
import numpy as np
import queue

#import Radar
import Class_Thread

# Main method for initiating and running radar measurements, signal processing and sending data through bluetooth to application.


def main():
    radar_queue = queue.Queue()
    interrupt_queue = queue.Queue()
    #heart_rate_queue = queue.Queue()
    #resp_rate_queue = queue.Queue()

    #radar = Radar.Radar(radar_queue, interrupt_queue)
    # radar.start()

    radar = Class_Thread.Radar(radar_queue, interrupt_queue)
    radar.get_data()

    # signalprocessing = Signalprocessing(radar_queue,heart_rate_queue,resp_rate_queue)
    # signalprocessing.start()

    # bluetooth = Bluetooth(heart_rate_queue,resp_rate_queue)
    # bluetooth.start()


if __name__ == "__main__":
    main()
