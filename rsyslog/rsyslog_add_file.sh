#!/bin/bash
#Description:add nginx syslogs and program syslogs to rsyslogd config
#Author:forverliu2015@gmail.com

today=`date +%F`
yesday=`date +%F -d '-1 days'`
now=`date +%F_%T`
hour=`date +%H`
libdir="/var/lib/rsyslog"

ngx_dir="/data/rsyslogs/nginx"
ngx_conf="/etc/rsyslog.d/nginx.conf"
prg_dir="/data/rsyslogs"
prg_conf="/etc/rsyslog.d/program.conf"

zero=0
one=1
sleep_time=3
restart_sys="False"

[ $hour -eq $one ] && sleep_time=60 && restart_sys="True"
#[ -f $ngx_conf ]&&cp $ngx_conf ${ngx_conf}_${now}
#[ -f $prg_conf ]&&cp $prg_conf ${prg_conf}_${now}

### remove yesterday domian ngx_conf
sed -i "/$yesday/,+7d" $ngx_conf
sed -i "/$yesday/,+7d" $prg_conf

### remove yesterday rsyslog lib
cd $libdir
old_files=`egrep "$yesday" *|awk -F: '{print $1}'`
for old_file in $old_files
do
	sleep_time=60
	if [ -f $old_file ] && [[ $old_file =~ "N+" ]];then
		find ./ -name $old_file -delete
	elif [ -f $old_file ] && [[ $old_file =~ "P+" ]];then
		find ./ -name $old_file -delete
	fi
done

function add_nginx() {
###  add today domain ngx_conf
    names=`ls $1`

    for name in $names
    do
	num=0
	access="${1}/${name}/${today}_access.log"
	error="${1}/${name}/${today}_error.log"
	if [ -f $access ] || [ -f $error ];then
	    if [ $name == "nginxServer" ];then
    		domain="nginxServer"
	    else
		name_reg=`echo $name|sed  's#_#[.-]#g'`
		#nginx_file=`egrep -R "$name" /etc/nginx/*|head -1|awk -F: '{print $1}'`
		nginx_file=`find /etc/nginx/ -name "*.conf"|xargs grep "$name"|head -1|awk -F: '{print $1}'`
		domain=`egrep "\s*server_name\s+${name_reg}" $nginx_file|head -1|tr ';' ' '|awk '{print $2}'`
		echo "$access:$domain"

		tag_len=24
		tag_len2=27
		if [ ${#domain} -gt $tag_len2 ];then
			domain=`echo ${domain:0:24}`
		elif [ ${#domain} -gt $tag_len ];then
			domain=`echo ${domain}|sed 's#.com##g'`
		fi
	    fi

		acc_tag="N+${domain}+access"
		err_tag="N+${domain}+error"

		[ -f $ngx_conf ] && num=`grep $domain $ngx_conf |wc -l`
		if [ $num -lt $one ];then
			cat >> $ngx_conf << EOF
\$InputFileName $access
\$InputFileTag $acc_tag
\$InputFileStateFile $acc_tag
\$InputFileSeverity debug
\$InputFileFacility local6
\$InputFilePollInterval 1
\$InputFilePersistStateInterval 25000
\$InputRunFileMonitor

\$InputFileName $error
\$InputFileTag $err_tag
\$InputFileStateFile $err_tag
\$InputFileSeverity debug
\$InputFileFacility local6
\$InputFilePollInterval 1
\$InputFilePersistStateInterval 25000
\$InputRunFileMonitor

EOF
		restart_sys="True"
		fi
	fi
    done
}

function add_program() {
###  add today name config
    names=`ls $1 |grep -v "nginx"`

    for name in $names
    do
	prog_dir="$1/${name}"
	[ ! -d $prog_dir ] && continue
	cd $prog_dir
	for env in `ls`
	do
			num=0
            log_file="${prog_dir}/${env}/${today}.log"
            if [ -f $log_file ];then
                echo "$log_file:$name"
                tag_len=27
                if [ ${#name} -gt $tag_len ];then
                        name=`echo ${name:0:27}`
                fi

                tag="P+${name}+${env}"
				[ -f $prg_conf ] && num=`grep $tag $prg_conf |wc -l`
                if [ $num -eq $zero ];then
                        cat >> $prg_conf << EOF
\$InputFileName $log_file
\$InputFileTag $tag
\$InputFileStateFile $tag
\$InputFileSeverity debug
\$InputFileFacility local6
\$InputFilePollInterval 1
\$InputFilePersistStateInterval 25000
\$InputRunFileMonitor

EOF
		restart_sys="True"
                fi
            fi
	done
    done
}

function chk_restart() {
	rsyslogd -N1
	if [ $? -eq $zero ];then
		if [ $restart_sys == "True" ];then
			/etc/init.d/rsyslog stop
			sleep $sleep_time
			/etc/init.d/rsyslog start
			echo "rsyslogd restarted"
		fi
	else
		echo "/etc/rsyslogd.conf error,please check"
	fi
}

add_program $prg_dir
add_nginx $ngx_dir
chk_restart
