import sys
import shelve
import matplotlib.pyplot as plt
import datetime

db = shelve.open('data.shelve', flag='r')
y = db['data']
x = range(0, len(y))
db.close()

fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(x, y)
ax.set_ylim(0, 255)

plt.show()
