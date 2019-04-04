import threading
import time
import numpy
import queue

class HeartRate (threading.Thread):
     def __init__(self, HR_filter_queue, heart_rate_queue):
          self.HR_filter_queue = HR_filter_queue
          self.heart_rate_queue = heart_rate_queue
          super(HeartRate, self).__init__()  # Inherit threading vitals

     def run(self):
          if self.HR_filter_queue.qsize() >= 3:
               for i in range(3):
                    data = self.HR_filter_queue.get()
                    self.heart_rate_queue.put(data)
          pass


class RespiratoryRate (threading.Thread):
     def __init__(self, RR_filter_queue, respiratory_rate_queue):
          self.RR_filter_queue = RR_filter_queue
          self.respiratory_rate_queue = respiratory_rate_queue
          super(RespiratoryRate, self).__init__()  # Inherit threading vitals

     def run(self):
          if self.RR_filter_queue.qsize() >= 4:
               for i in range(4):
                    data = self.RR_filter_queue.get()
                    self.respiratory_rate_queue.put(data)
          pass

##### MAIN #########

HR_filter_queue = queue.Queue()
heart_rate_queue = queue.Queue()
RR_filter_queue = queue.Queue()
respiratory_rate_queue = queue.Queue()

for i in range(3):
     HR_filter_queue.put("HR"+str(i))
     RR_filter_queue.put("RR"+str(i))

heart_rate = HeartRate(HR_filter_queue, heart_rate_queue)
heart_rate.start()

respiratory_rate = RespiratoryRate(RR_filter_queue, respiratory_rate_queue)
respiratory_rate.start()

print(list(heart_rate_queue.queue))
print(list(respiratory_rate_queue.queue))
