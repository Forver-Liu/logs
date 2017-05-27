#!/usr/bin/env python
#coding:utf-8

import time

while True:
  with open('zabbix.log','a') as log:
	dt = time.strftime('%Y-%m-%d %H:%M:%S')
	logdt = "[" + dt + ",000]"
	logco = " ###########" + '\n'
	cons = logdt + logco
	print cons

	log.write(cons)
	time.sleep(5)
