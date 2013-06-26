import sys
import shelve
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime

def add_subplot(id, x, y, lim1, lim2):
    ax = fig.add_subplot(id)
    #ax.plot(x, data['temp'], 'b-', x, data['hum'], 'g-')
    ax.plot(x, y)
    # format the ticks
    locator = mdates.AutoDateLocator()
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.AutoDateFormatter(locator))
    ax.xaxis.set_minor_locator(locator)
    datemin = x[0]
    datemax = x[-1]
    ax.set_xlim(datemin, datemax)
    ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
    ax.grid(True)
    ax.set_ylim(lim1, lim2)
    # rotates and right aligns the x labels, and moves the bottom of the
    # axes up to make room for them

db = shelve.open('data.shelve', flag='r')
x = []
data = {}
lim = {}
last = {}
for d in db['data']:
    x.append(d['t'])
    for k in ['t1', 't2', 't3', 'lowbat']:
        if data.has_key(k) == False:
            data[k] = []
            lim[k] = [-99, -99]
            last[k] = 0
        if d[k] < -100:
            d[k] = last[k]
        if (d[k] < lim[k][0])or(lim[k][0] == -99):
            lim[k][0] = d[k]
        if (d[k] > lim[k][1])or(lim[k][1] == -99):
            lim[k][1] = d[k]
        data[k].append(d[k])
        last[k] = d[k]
db.close()

fig = plt.figure()
add_subplot(311, x, data["t1"], lim["t1"][0] - 1, lim["t1"][1] + 1)
add_subplot(312, x, data["t2"], lim["t2"][0] - 1, lim["t2"][1] + 1)
add_subplot(313, x, data["t3"], lim["t3"][0] - 1, lim["t3"][1] + 1)
fig.autofmt_xdate()

plt.show()
