# Extracting Browser History

Note: These scripts have been written & tested in 2018, they probably still work but if there were major changes to the history database they won't work anymore.

## Obtaining the history file

The browser history of Firefox and Chrome, as well as their variants (I used the scripts with Waterfox and Chromium), are usually stored in SQLite databases. In this case, these are just files somewhere in your home directory.

* Firefox, under Linux, stores te database in `$HOME/.mozilla/firefox/PROFILE/places.sqlite` - replace PROFILE by your profile name.
* Chromium, under Linux, stores the database in `$HOME/.config/Default/History` (replace Default by the profile name if you have multiple).


### Firefox and forks (e.g. Waterfox)

You can use the following SQL commands, courtesy of cor-el on the [Mozilla Support Forum](https://support.mozilla.org/de/questions/835204) (CC-BY-SA) to extract the browsing history from the places.sqlite file:

    SELECT datetime(moz_historyvisits.visit_date/1000000,'unixepoch'), moz_places.url, moz_places.title
    FROM moz_places, moz_historyvisits
    WHERE moz_places.id = moz_historyvisits.place_id

You can use a normal sqlite program (e.g. `sqlite3` under Linux) or the sqlite-manager addon (it lets you save the results as CSV using the Actions button).

### Chromium / Chrome

For Chromium I used these SQL commands, courtesy of Traveling Tech Guy on [superuser](https://superuser.com/questions/602252/can-chrome-browser-history-be-exported-to-an-html-file) (CC-BY-SA) to extract the history. I used the `sqlite3` program on Linux to access the database:

    $ sqlite3 History
    sqlite> .headers on
    sqlite> .mode csv
    sqlite> .output my-history.csv
    sqlite> SELECT datetime(last_visit_time/1000000-19644473600,'unixepoch','localtime'), url FROM urls ORDER BY last_visit_time DESC

The output of these commands will be saved in `my-history.csv`.

## Parse CSV

Finally, you might want to extract the interesting data (for me that is time stamp and page URL) from the CSV files. This is not completely trivial as, in the case of Firefox, the CSV contains the page title wich can include funny symbols and unclosed quotes (really annoying!).

I wrote a script `extract_fox.py` that works in most cases (only skips lines containing `","` (including the quotes) and the last line). The first part of the script parses the CSV, the 2nd one prints out the history. For simplicity, I use the UNIX Epoch as time stamp (seconds since 1970).

The chromium script is very easy since it only contains time/url, it prints the history in the same format.

# Firefox JSON Password Parser

Note: This has been written and tested in 2018. The password interface in Firefox has changed significantly recently, I'm not sure if this code still works.


Firefox doesn't have a built-in export function for passwords and the password export addon I used in the past stopped working with Firefox Quantum. This is why I searched for a manual method to extract the passwords.

## Exporting passwords from Firefox

You can use the internal console to achieve this task. I follow & summarize the guide by cor-el (again!) from the [Mozilla Support Forum](https://support.mozilla.org/de/questions/1077630#answer-834769), the code below is his (under CC-BY-SA).

Set `devtools.chrome.enabled` to `true` in `about:config` and open the console ("Browser Konsole" in German) via 3-bar menu -> Web Developer (or Ctrl+Shift+J). Then paste the following javascript code (I advise you to read all code that you paste into your browser, especially if it is concerning passwords):

    /* export the names and passwords in JSON format to firefox-logins.json */
    var tokendb = Cc["@mozilla.org/security/pk11tokendb;1"].createInstance(Ci.nsIPK11TokenDB);
    var token = tokendb.getInternalKeyToken();
    
    try {token.login(true)} catch(e) {Cu.reportError(e)}
    
    if (!token.needsLogin() || token.isLoggedIn()) {
     var passwordmanager = Cc["@mozilla.org/login-manager;1"] .getService(Ci.nsILoginManager);
     var signons = passwordmanager.getAllLogins({});
     var json = JSON.stringify(signons, null, 1);
    
     var ps = Services.prompt;
     var txt = 'Logins: ' + signons.length;
     var obj = new Object; obj.value = json;
    
     if (ps.prompt(null, 'Logins - JSON', txt, obj, null, {})){
     var fp=Cc["@mozilla.org/filepicker;1"].createInstance(Ci.nsIFilePicker);
     fp.init(window,"",Ci.nsIFilePicker.modeSave);
     fp.defaultString = "firefox-logins.json";
    
     fp.open((rv) => {
     if (rv == Ci.nsIFilePicker.returnOK || rv == Ci.nsIFilePicker.returnReplace) {
     var fos = Cc['@mozilla.org/network/file-output-stream;1'].createInstance(Ci.nsIFileOutputStream);
     fos.init(fp.file, 0x02 | 0x08 | 0x20, 0666, 0);
     var converter = Cc['@mozilla.org/intl/converter-output-stream;1'].createInstance(Ci.nsIConverterOutputStream);
    
     converter.init(fos, 'UTF-8', 0, 0);
     converter.writeString(json);
     converter.close();
    }})
    }}

Just store the JSON output in some file, e.g. `passwords.json`.

## Parsing the passwords json file

Since the json file is optimized for machines rather than humans it would be nice to convert it e.g. to a CSV file that can be important into a spreadsheet. I wrote the following script to convert the json file (read from stdin) and print out comma separated values (CSV) to stdout. You can read & write to files like this: `cat passwords.json | python3 firefox_password_parser.py > pws.csv`. It creates a CSV file containing URL, Username and Password. Additionally, it separates the URL into 2 parts (`https://www.` and `example.com`) and alphabetically sorts them by second level domain.

If you want to copy the script without downloading, here you go:

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



I'm happy about any feedback, questions or remarks. Feel free to contact me here or (preferrably) via email. Also feel free share & change my code under the MIT/X11 license, the superuser and Mozilla forum snippets are licensed under creative commons (CC BY-SA, see respective websites for more info).