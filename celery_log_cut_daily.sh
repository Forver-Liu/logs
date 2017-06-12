#!/bin/bash
# Description: split celery/celerybeat log by remove file daily

yesday=`date -d "-1 days" +%F`
logs=`ps -ef|grep celery|grep -v grep|tr ' ' '\n'|grep "\-\-logfile="|awk -F= '{print $2}'|sort -bu`

for file in $logs
do
	echo $file
	newfile=`echo $file|sed s/\.log$/-${yesday}\.log/g`
	echo "NEW file:$newfile"
#	mv $logs $newfile
done
