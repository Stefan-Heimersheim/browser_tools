import numpy as np
import datetime
import time
import sys
import csv

history=[]

with open(sys.argv[1],'r') as f:
    next(f)
    for line in f:
        content = line.split(',')
        assert( np.shape(content) == (2,) )
        t = content[0].strip('\"')
        url = content[1].strip('\n')
        history.append([t, url])

# In the end, write a CSV with $EPOCH $URL
print("EPOCH URL")
for h in history:
    # Parse the date
    dateString = h[0]
    date = datetime.datetime.strptime(dateString,'%Y-%m-%d %H:%M:%S')
    print(str(time.mktime(date.timetuple()))+" "+h[1])
