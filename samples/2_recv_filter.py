'''
A simple exmaple to recv data from can bus, and apply filter settings
'''

import sys
import time

from canbus import Can, CanError

# setup
can = Can()

# initilize
ret = can.begin()
if ret != CanError.ERROR_OK:
    print("Error to initilize can!")
    sys.exit(1)
print("initlized succesufully!")

# configure masks & filters (optional)
mask=0x3FF
filter_can_id=0x000
## set1
can.init_mask(0, False, mask)
can.init_filter(0, False, filter_can_id)
can.init_filter(1, False, filter_can_id)
## set2
can.init_mask(1, False, mask)
can.init_filter(2, False, filter_can_id)
can.init_filter(3, False, filter_can_id)
can.init_filter(4, False, filter_can_id)
can.init_filter(5, False, filter_can_id)
print('masks&filtes configured')

# receive
while True:
    if can.checkReceive():
        error, msg = can.recv()
        if error == CanError.ERROR_OK:
            print("can id", msg.can_id)
            print("is rtr frame", msg.is_remote_frame)
            print("is eff frame", msg.is_extended_id)
            print("can data", msg.data)
            print("can data dlc", msg.dlc)
            print("RX  {}".format(msg))
    else:
        time.sleep(0.1)


