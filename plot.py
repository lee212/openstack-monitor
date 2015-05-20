"""
WIP
"""

import matplotlib.pyplot as plt
import numpy as np
import time


def vlocaltime(seconds):
    return np.array(map(time.localtime, seconds))


def plocaltime(t):
    return time.strftime('%H:%M', t)

times = np.loadtxt('times.txt', delimiter=',').T
localtimes = map(plocaltime, vlocaltime(times[0]))

plt.scatter(times[0], times[1], marker='.')

ticks = plt.gca().get_xticks().tolist()
localtimes = map(plocaltime, vlocaltime(ticks))
plt.xticks(ticks, localtimes, rotation='vertical')
plt.xlabel('Time of Day')
plt.ylabel('Response Time (seconds)')
plt.savefig('/tmp/times.png', bbox_inches='tight')
