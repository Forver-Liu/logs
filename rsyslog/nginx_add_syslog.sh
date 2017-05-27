#!/bin/bash
#Description:add nginx access\error log to syslog

function add_sys() {
    config=$1
    echo $config
    server_name=`grep server_name $config |awk '{print $2}'|sed "s/;//g"|sed "s/ //g"`
    server_name=`echo $server_name|tr '-' '_'|tr '.' '_'`
    echo $server_name

    emerg=24
    if [ ${#server_name} -gt $emerg ];then
	server_name=`echo ${server_name:0:32}`
    fi
    
    if [ -n $server_name ];then
        acc_syslog=`echo -e "\taccess_log  syslog:server=127.0.0.1:514,facility=local1,tag=${server_name}BaccessB,severity=info main;"`
        err_syslog=`echo -e "\terror_log  syslog:server=127.0.0.1:514,facility=local1,tag=${server_name}BerrorB,severity=debug crit;"`

        sed -i "/        access_log \/var\/log\/nginx/a ${acc_syslog}" $config
        sed -i "/        error_log \/var\/log\/nginx/a ${err_syslog}" $config

    else
        echo -e "\tERROR:$1"
    fi  
}

for file in `find /etc/nginx/conf.d/ -name "*.conf"`
do
    one=1
    num=`cat $file|grep "syslog"|wc -l`
    if [ $num -gt $one ];then
        echo "Done:$file"
    else
        add_sys $file
    fi  
done
