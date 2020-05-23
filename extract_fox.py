import numpy as np
import datetime
import time
import sys
import csv

history=[]

for line in open(sys.argv[1],'r'):
    pass
lastLine = line

for line in open(sys.argv[1],'r'):
    if line[-3] == '"' and line[-2] == ',' and line[-1] == '\n':
        col = 2
        #[1:-3] removes first quote and lasquote+lostcomma+newline
        newLine = line[1:-3].replace('","','\n').splitlines()
    elif line[-2] == '"' and line[-1] == '\n':
        col = 3
        #[1:-2] removes first quote and lasquote+newline
        newLine = line[1:-2].replace('","','\n').splitlines()
    elif line == lastLine:
        print("Skipping the last line.")
        continue
    else:
        print("ERROR in the following line:")
        print(line)
        continue
    if np.shape(newLine) != (col,):
        print("ERROR, shape mismatch with this line:")
        print(line)
        continue
    history.append(newLine)

# In the end, write a CSV with $EPOCH $URL
print("EPOCH URL")
for h in history:
    # Parse the date
    dateString = h[0]
    date = datetime.datetime.strptime(dateString,'%Y-%m-%d %H:%M:%S')
    print(str(time.mktime(date.timetuple()))+" "+h[1])

