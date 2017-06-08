#!/bin/bash
# Description: deal nginx access and nginx log daily

yes_day_A=`date +%d/%b/%Y -d -1day`
yes_day_A1=`date +%d"\/"%b"\/"%Y -d -1day`
yes_day_E=`date +%Y/%m/%d -d -1day`
yes_day_E1=`date +%Y"\/"%m"\/"%d -d -1day`
yes_day=`date +%Y%m%d -d -1day`
mon=`date +%Y%m`

file_list=`find /etc/nginx/ -type f -name "*.conf" -print0 | xargs -0 egrep '^(\s|\t)*access_log|error_log'|awk '{print $3}'|tr ";" " "|tr '\n' ' '`
#file_list=`ls *.log`

for file in $file_list
do
	site=`echo $file |awk -F"log$" '{print $1}'`
	count=0

	if [ -f $file ];then
		echo "Log file found:$file"
		path=`dirname $file`
		cd $path && find ./ -name "*[0-9].log.zip" -mtime +30 -delete
		test ! -d $mon && mkdir $mon
		site_name=`basename ${file} |sed 's/log//g'`

		if [[ $file =~ .*acc.* ]];then
			date_fmt="\[$yes_day_A:"
			date_str="\[$yes_day_A1:"
			echo -e "\taccess_file:$file"
			#continue
		elif [[ $file =~ .*err.* ]];then
			date_fmt="^$yes_day_E"
			date_str="^$yes_day_E1"
			echo -e "\terror_file:$file"
			#continue
		fi

		dst_file="${site_name}${yes_day}.log"
		grep "$date_fmt" $file >$dst_file
		[ $? -ne 0 ] && let count=count+1

		sleep 5
		nfile_size=`ls -l $dst_file |awk '{print $5}'`
		if [ $nfile_size -gt 1024 ];then
			zip -m -r ${dst_file}.zip $dst_file
			mv ${dst_file}.zip $mon/
		elif [ $nfile_size -le 10 ];then
			rm -f $dst_file
		else
			mv $dst_file $mon/
		fi
		[ $? -ne 0 ] && let count=count+1
		
		sleep 5
		if [ $count -eq 0 ];then
			sed -i "/$date_str/d" $file
			sed -i "/^$/d" $file
		fi
	fi
done

nginx -t
[ $? -eq 0 ] && nginx -s reload
