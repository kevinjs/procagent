#!/usr/bin/env python

from __future__ import division
import random
import time

for j in range(2, 8):
    startT = time.clock()
    counter = 0
    for i in range(10 ** j):
        x = random.uniform(-1, 1)
        y = random.uniform(-1, 1)
        if x**2 + y**2 < 1:
            counter += 1
    endT = time.clock()
    print (4 * (counter / 10 ** j))
    print (endT - startT)
    print "*" * 10
