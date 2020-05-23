#!/usr/bin/env python

import sys
import json
import numpy as np

json=json.load(sys.stdin)
uList = []
pwList = []
urlList = []
for a in json:
    # Split into domain, tld, etc.
    line = a['hostname'].strip().split('.')
    recent = [e+'.' for e in line if e and line.index(e) != len(line)-1]
    recent.append(line[-1])

    # Handle cases that are not something.domain.tld
    # Sadly doesn't handly ...co.uk etc., have to do manually
    if len(recent) != 3:

        # Assume stuff starts with something://, fail assertion otherwise
        recent[0] = recent[0].split('//')
        assert(len(recent[0])==2)
        recent[0][0] = recent[0][0]+'//'

        # Deal with different cases
        if np.shape(recent) == (1,2): #http://localhost:631
            recent = [recent[0][0],recent[0][1],' ']
        if np.shape(recent) == (2,): #https://example.com
            recent = [recent[0][0],recent[0][1],recent[1]]
        if len(recent) >= 4: #https://www.login.service.example.com
            recent = [recent[0][0]+recent[0][1]+''.join(recent[1:-2]),recent[-2],recent[-1]]
    # urlList contains array [stuff, domain, tld], uList and pwList just usernames and pws respectively        
    urlList.append(recent)
    uList.append(a['username'])
    pwList.append(a['password'])

# Sort by domain
urlList = np.array(urlList)
sortList = []
for a in urlList:
    sortList.append(a[1])
sortList = np.array(sortList)
indices = np.argsort(sortList)
uList = np.array(uList)
pwList = np.array(pwList)

# Print as csv with delimiter | since , often in pws
for i in indices:
    output = urlList[i][0]+'|'+urlList[i][1]+urlList[i][2]+'|'+uList[i]+'|'+pwList[i]
    print(output.encode('utf-8').decode())
