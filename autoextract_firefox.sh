#!/bin/bash
IFS=$'\n'
if [ -z "$1" ]; then
	path="$HOME/.mozilla/firefox/"
else
	path="$1"
fi
echo "Searching databases in $path"
for database in $(find $path -name 'places.sqlite');
do
	echo "Database" $database
	profilename=$(echo $database | rev | cut -d / -f 2 | rev)
	echo $profilename
	outname="history-firefox_$(date +%F_%H-%M-%S)_$profilename"
	echo $outname
	echo ".headers on
.mode csv
.output $outname.csv
SELECT moz_historyvisits.visit_date, moz_places.url, moz_places.title

FROM moz_places, moz_historyvisits
WHERE moz_places.id = moz_historyvisits.place_id;" | sqlite3 $database 
	echo "Done"
done
# The time is seconds since (Linux) Epoch (1970) in microseconds.
# Other, less accurate, options:
#SELECT strftime('%Y-%m-%d %H:%M:%f',moz_historyvisits.visit_date/1000000.0,'unixepoch'), moz_places.url, moz_places.title
#SELECT datetime(moz_historyvisits.visit_date/1000000,'unixepoch'), moz_places.url, moz_places.title
