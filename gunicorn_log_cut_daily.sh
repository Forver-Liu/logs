#!/bin/bash
# Description:splid gunicorn log by move file and reload process daily

today=`date +%F`
pids=`ps -ef|grep gunicorn|awk '{if($3==1)print $2}'`
for pid in $pids
do
	echo "PID:$pid"
	cmd=`ps aux|grep $pid|grep -v grep|awk '{for(i=1;i<11;i++)$i="";print $0}'`
	cmd=`echo $cmd`
	echo "CMD:$cmd"
	access_logfile=`echo $cmd|tr ' ' '\n'|grep "access-logfile"|awk -F= '{print $2}'`
	error_logfile=`echo $cmd|tr ' ' '\n'|grep "error-logfile"|awk -F= '{print $2}'`
	echo "ACCESS log:$access_logfile"
	echo "ERROR log:$error_logfile"

	cwd=`readlink -f /proc/$pid/cwd`
	cd $cwd

	if [ -s $access_logfile ];then
		newfile=`echo $access_logfile|sed s/\.log$/-${today}\.log/g`
		echo "NEW file:$newfile"
		mv $access_logfile $newfile
	fi
	
	if [ -s $error_logfile ];then
		newfile=`echo $error_logfile|sed s/\.log$/-${today}\.log/g`
		echo "NEW file:$newfile"
		mv $error_logfile $newfile
	fi

	kill -15 $pid
	eval $cmd
done
