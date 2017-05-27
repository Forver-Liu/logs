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
config.read("sumlog_server.conf")
sections = config.sections()

host = config.get('main','host')
port = config.getint('main','port')
path = config.get('main','path')
path = path if path.endswith('/') else path + "/"
conn = MongoClient(host=host,port=port)
db = conn["logs"]

today = time.strftime('%Y-%m-%d')
yesday = time.strftime('%Y-%m-%d',time.localtime(time.time() - 24*60*60))

pl = r'^\[(?P<logtime>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})\] (?P<content>.*)$'
pt = re.compile(pl)


if not os.path.exists(path):
	os.makedirs(path)

def dump_log(new_log,db_col,logtype):
	yes_cols = db_col.find({"logtime":{'$lt':today + " 00:00:00000"},"type":logtype}).count()
	tod_cols = db_col.find({"logtime":{'$gt':today + " 00:00:00000"},"type":logtype}).count()
	if yes_cols > 1:
		new_log_name = new_log + "_" + yesday + '.log'
		dump_file = open(new_log_name,"a+")
		for col in db_col.find({"logtime":{'$lt':today + " 00:00:00000"},"type":logtype},{"content":1}).sort("logtime"):
			col_con = col['content'].encode('utf-8')
			dump_file.write(col_con)
		dump_file.close()
		db_col.remove({"logtime":{'$lt':today + " 00:00:00000"},"type":logtype})

	if tod_cols > 1:
		new_log_name = new_log + "_" + today + '.log'
		dump_file = open(new_log_name,"a+")
		for col in db_col.find({"logtime":{'$gt':today + " 00:00:00000"},"type":logtype,"dumped":0},{"content":1,"_id":1}).sort("logtime"):
			col_con = col['content'].encode('utf-8')
			db_col.update({"_id":col['_id']},{'$set':{"dumped":1}})
			dump_file.write(col_con)
		dump_file.close()

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

		pathlog = path + name + '/' + env + '/'
		if not os.path.exists(pathlog):
			os.makedirs(pathlog)
		new_log = pathlog + logname

		dump_log(new_log,db_col,logtype)
		time.sleep(30)
