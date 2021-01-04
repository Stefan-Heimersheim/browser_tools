#!/bin/bash
IFS=$'\n'
if [ -z "$1" ]; then
	path="$HOME/.config/chromium/"
else
	path="$1"
fi
echo "Searching databases in $path"
for database in $(find $path -name 'History');
do
	echo "Opening file" $database
	profilename=$(echo $database | rev | cut -d / -f 2 | rev)
	if [[ "$profilename" == 'System Profile' ]]; then
    	echo "Skipping $profilename"
    	continue
  	fi
  	echo "Reading $profilename"
	detoxprofilename=$(echo $profilename | detox --inline)
	outname="history-chrome_$(date +%F_%H-%M-%S)_$detoxprofilename"
	echo "Writing to $outname"
	echo ".headers on
.mode csv
.output $outname.csv
SELECT visits.visit_time-11644473600000000, urls.url, urls.title

FROM visits, urls
WHERE urls.id = visits.url;" | sqlite3 $database 
	echo "Done"
done
# Chromium saves the time in microseconds (1e-6 s) since 1601 (like Windows Epoch), convert to Linux Epoch (since 1970) in microseconds.