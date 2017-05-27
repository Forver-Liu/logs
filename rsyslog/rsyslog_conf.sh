#!/bin/bash
# Description: set rsyslog to summery nginx and programs logs
# Author:forverliu2015@gmail.com

config="/etc/rsyslog.conf"
inif_file="/etc/init.d/rsyslog"
rsyslog_server="10.10.53.29"
zero=0

if [ ! -f $config ];then
	echo "please check the rsyslog is installed"
	exit 1
fi

if [ ! -f $inif_file ];then
	echo "$inif_file needs upload mannual"
	exit 1
fi

mv $config ${config}-ori
cat >> $config << EOF
#### MODULES ####
\$ModLoad imuxsock
\$ModLoad imklog
\$ModLoad imfile
\$ModLoad imudp
\$UDPServerRun 514
\$MaxMessageSize 256k

#### GLOBAL DIRECTIVES ####
\$ActionFileDefaultTemplate RSYSLOG_TraditionalFileFormat
\$WorkDirectory /var/lib/rsyslog
\$IncludeConfig /etc/rsyslog.d/*.conf
\$FileOwner root
\$FileGroup root
\$DirOwner root
\$DirGroup root
\$FileCreateMode 0644
\$DirCreateMode 0755
\$Umask 0022

#### RULES ####
*.info;mail.none;authpriv.none;cron.none;local1.none;local0.none;local6.none    /var/log/messages
authpriv.*                                              /var/log/secure
mail.*                                                  -/var/log/maillog
cron.*                                                  /var/log/cron
*.emerg                                                 *
uucp,news.crit                                          /var/log/spooler
local7.*                                                /var/log/boot.log

\$template msg,"%msg:2:$%\n"
\$template msgTime,"%timegenerated:8:15% %msg:2:$%\n"
\$template fileLprog,"/data/rsyslogs/%HOSTNAME%/%syslogtag%/%\$year%-%\$month%-%\$day%.log"
\$template fileLnginx,"/data/rsyslogs/nginx/%syslogtag:F,66:1%/%\$year%-%\$month%-%\$day%_%syslogtag:F,66:2%.log"

local0.*                                                -?fileLprog;msgTime
local1.*                                                -?fileLnginx;msg
#local6.*        @@${rsyslog_server}:514
if \$syslogfacility-text == 'local0' then @@(z5)${rsyslog_server}:514
if \$syslogfacility-text == 'local1' then @@(z5)${rsyslog_server}:514
EOF

rsyslogd -N1
if [ $? -eq $zero ];then
	$inif_file stop
	sleep 3
	$inif_file start
else
	echo "config error,please check..."
fi
