#!/usr/bin/env python
#coding:utf-8

import subprocess
import time

p = subprocess.Popen('tail -F zabbix.log', shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE,)

while True:
    line = p.stdout.readline()
    if line:
         print line
