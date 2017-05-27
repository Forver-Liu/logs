#!/usr/bin/env python
#coding:utf-8

from __future__ import division
import urllib2
import time

bs_url = "http://ip.taobao.com/service/getIpInfo.php?ip="

region_dic = { }

def get_data(IP,WIGHT=1):

	city = ""
	area = ""
	country = ""
	region = ""
	isp = ""

	request = urllib2.Request(bs_url+IP)
	reponse = urllib2.urlopen(request)
	#print result
	result = eval(reponse.read())
	#print result
	
	code = result['code']
	country_id = result['data']['country_id']
	#print country_id

	if code == 0:
		if country_id == 'CN':
			city = result['data']['city'].decode('unicode-escape')
			area = result['data']['area'].decode('unicode-escape')
			country = result['data']['country'].decode('unicode-escape')
			region = result['data']['region'].decode('unicode-escape')
			isp = result['data']['isp'].decode('unicode-escape')
		else:
			region = u"国外"
		#print region
		if region not in region_dic.keys():
			region_dic['%s'%region] = { }
		region_dic['%s'%region]['%s'%IP] = int(WIGHT)
	else:
		print "request error"

	print "IP:%s\nCity:%s\nArea:%s\nCountry:%s\nRegion:%s\nISP:%s"%(IP,city,area,country,region,isp)

if __name__ == '__main__':
	count = -1
	ip_list = []
	fo = open('ip_sort_0713.txt','r')
	for line in fo.readlines():
		wight,ip = line.strip().split()
		try:
			get_data(ip,wight)
		except Exception as e:
			continue
		print wight,":",ip
		count += int(wight)
		time.sleep(0.5)
	fo.close()

	print u'合计：'
	for regions,stats in region_dic.items():
		times = 0
		for time in stats.values():
			times += time
		print "%s:%.2f"%(regions.encode('utf-8'),int(times)/count)
