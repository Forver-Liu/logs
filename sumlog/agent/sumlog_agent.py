#!/usr/bin/env python2.7
#coding:utf-8

import ConfigParser
import os,sys
import time
import re,glob
import pickle
import subprocess,commands
from pymongo import MongoClient

config = ConfigParser.ConfigParser()
config.read("sumlog_agent.conf")
sections = config.sections()

host = config.get('main','host')
port = config.getint('main','port')
conn = MongoClient(host=host,port=port)
db = conn["logs"]

today = time.strftime('%Y-%m-%d')
yesday = time.strftime('%Y-%m-%d',time.localtime(time.time() - 24*60*60))

pl = r'^\[(?P<logtime>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})\] (?P<content>.*)$'
pt = re.compile(pl)

try:
	file_seek = pickle.load(open('seeks.pik','r'))
except Exception as e:
	file_seek = {}

def insert_log(logfile,db_col,logtype):
	with open(logfile,'r') as logs:
		getseek = file_seek[logfile]['seek']
		getline = file_seek[logfile]['line']
		logs.seek(int(getseek),0)

		logtimes = ''
		contents = ''
		for line in logs:
			pattern = pt.search(line)
			if pattern and pattern.group('logtime').split()[0] in [yesday,today]:
				if logtimes and contents:
					db_col.insert({"logtime":logtimes, "type":logtype, "content":contents, 'dumped':0})
					logtimes = ''
					contents = ''
				logtimes = pattern.group('logtime')

			if contents:
				contents = contents + line
			else:
				contents = line

			getline = getline + 1

		if logtimes and contents:
			db_col.insert({"logtime":logtimes, "type":logtype, "content":contents, 'dumped':0})

		file_seek[logfile]['seek'] = logs.tell()
		file_seek[logfile]['line'] = getline 

def insert_using(logfile,db_col_cur,logtype):
	if file_seek[logfile]['using'] == 0:
		return
		
	line_num = file_seek[logfile]['line']
	logtimes = ''
	contents = ''
	while True:
		cmd1 = "sed -n '%d,%d p' %s"%(line_num,line_num+9,logfile)
		cmd2 = "sed -n '%d,%d p' %s|wc -l"%(line_num,line_num+9,logfile)
		sts1,lines = commands.getstatusoutput(cmd1)
		sts2,wc_l = commands.getstatusoutput(cmd2)

		for line in lines.split('\n'):
			pattern = pt.search(line)
			if pattern and pattern.group('logtime').split()[0] == today:
				if logtimes and contents:
					db_col.insert({"logtime":logtimes, "type":logtype, "content":contents, 'dumped':0})
					logtimes = ''
					contents = ''
				logtimes = pattern.group('logtime')
			if contents:
				contents = contents + line
			else:
				contents = line

		count = int(wc_l)
		line_num = line_num + count
		file_seek[logfile]['line'] = line_num
		if count != 10:
			if logtimes and contents:
				db_col.insert({"logtime":logtimes, "type":logtype, "content":contents, 'dumped':0})
			break

	file_seek[logfile]['seek'] = os.path.getsize(logfile)

if __name__ == "__main__":
  while True:
	for section in sections[1:]:
		logfiles = config.get(section,'logfile')
		logtype = config.get(section,'type')
		env = config.get(section,'env')
		name = config.get(section,'name').replace('-','_')
		
		if len(logtype.strip()) > 0:
			logname = logtype.upper() + '_' + name + '_' + env
		else:
			logname = name + '_' + env
			logtype = None
		db_col = db[name + '_' + env]

		file_list = glob.glob(logfiles)
		for logfile in file_list:
			mtime = os.path.getmtime(logfile)
			mdate = time.strftime('%Y-%m-%d',time.localtime(mtime))
			dtime = time.time() - mtime
			fsize = os.path.getsize(logfile)

			if fsize < 27:
				continue

			if logfile not in file_seek.keys():
				file_seek[logfile] = {'date':mdate,'seek':0,'using':0,'line':1}

			if mdate == yesday:
				if file_seek[logfile]['date'] != yesday:
					file_seek[logfile]['date'] = yesday
					file_seek[logfile]['seek'] = 0
				insert_log(logfile,db_col,logtype)

			if mdate == today:
				if file_seek[logfile]['date'] != today:
					file_seek[logfile]['date'] = today
					file_seek[logfile]['seek'] = 0

				if dtime < 300:
			#		print "%s: file may be using"%logfile
					file_seek[logfile]['using'] = 1
					insert_using(logfile,db_col,logtype)
				else:
			#		print "%s: get today log"%logfile
					file_seek[logfile]['using'] = 0
					insert_log(logfile,db_col,logtype)
					
			pickle.dump(file_seek,open('seeks.pik','wb'))
			time.sleep(30)
