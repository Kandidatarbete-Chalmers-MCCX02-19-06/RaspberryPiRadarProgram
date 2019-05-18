import numpy as np
import threading
import time
import queue


class Filter (threading.Thread):

    def __init__(self, q):
        super(Filter, self).__init__()
        self.q = q

    def run(self):
        while True:
            print('The thread is running')
            time.sleep(1)
            if self.q.empty() == False:
                print('test')
                break


def main():
    q = queue.Queue()
    filter = Filter(q)
    filter.start()
    print('starting')
    time.sleep(10)
    q.put(1)
    print('stop')


if __name__ == "__main__":
    main()
