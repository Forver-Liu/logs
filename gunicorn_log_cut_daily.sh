#!/bin/bash
# Description:splid gunicorn log by move file and reload process daily

today=`date +%F -d "-1 days"`
pids=`ps -ef|grep gunicorn|awk '{if($3==1)print $2}'`
for pid in $pids
do
	echo "PID:$pid"
	cmd=`ps aux|grep "\<$pid\>"|grep -v grep|awk '{for(i=1;i<11;i++)$i="";print $0}'`
	cmd=`echo $cmd`
	echo "CMD:$cmd"
	access_logfile=`echo $cmd|tr ' ' '\n'|grep "access-logfile"|awk -F= '{print $2}'`
	error_logfile=`echo $cmd|tr ' ' '\n'|grep "error-logfile"|awk -F= '{print $2}'`
	echo "ACCESS log:$access_logfile"
	echo "ERROR log:$error_logfile"

	cwd=`readlink -f /proc/$pid/cwd`
	echo "CWD:$cwd"
	cd $cwd

	todo=0
	if [ -s $access_logfile ];then
		newfile=`echo $access_logfile|sed s/\.log$/-${today}\.log/g`
		echo "NEW file:$newfile"
		mv $access_logfile $newfile
		if [ $? -eq 0 ];then
			todo=1
		else
			todo=0
			echo "move $access_logfile failed"
			continue
		fi
	fi
	
	if [ -s $error_logfile ];then
		newfile=`echo $error_logfile|sed s/\.log$/-${today}\.log/g`
		echo "NEW file:$newfile"
		mv $error_logfile $newfile
		if [ $? -eq 0 ];then
			todo=1
		else
			todo=0
			echo "move $error_logfile failed"
			continue
		fi
	fi

	if [ $todo -eq 1 ];then
		echo "RESTARTING:$cmd"
#		kill -15 $pid
		ps aux|grep "$cmd"|grep -v grep|awk '{print $2}'|xargs kill -9
		sleep 3
		eval $cmd
		[ $? -ne 0 ]&& echo "restart failed,need check"
	fi
done
