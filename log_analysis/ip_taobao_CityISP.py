#!/usr/bin/env python
#coding:utf-8

from __future__ import division
import urllib2
import time
import sys,os
import pickle

bs_url = "http://ip.taobao.com/service/getIpInfo.php?ip="

ip_wiget_list = []
# Example = [{'ip1':1},{"ip2":2}]
region_dic = { }
# Example = {'fujian':{"ip":[wight,city,area,region,isp]}}
isp_dic = { }
# Example = {'dianxin':{'ip':[wight,city,area,region,isp]}}


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
			city = u'国外'
			area = u'国外'
			region = u"国外"
			isp = u"国外"
		#print region
		if region not in region_dic.keys():
			region_dic['%s'%region] = { }
		region_dic['%s'%region]['%s'%IP] = [int(WIGHT),city,area,region,isp]
		#print isp
		if isp not in isp_dic.keys():
			isp_dic['%s'%isp] = { }
		isp_dic['%s'%isp]['%s'%IP] = [int(WIGHT),city,area,region,isp]
	else:
		print "request error"

	print "IP:%s\nCity:%s\nArea:%s\nCountry:%s\nRegion:%s\nISP:%s"%(IP,city,area,country,region,isp)

def ip_sort(IP_FILE):
	data = open(IP_FILE,'r')
	ips = data.read()

	ips_list = ips.strip().split('\n')
	#ips_list = re.findall('(?:\d{1,3}\.){3}\d{1,3}',ips.strip())
	#print ips_list

	total = len(set(ips_list))
	ip_dic = {}
	# Example = {'127.0.0.1':1}
	for ip in set(ips_list):
		count = ips_list.count(ip)
		ip_dic[ip.strip()] = count

	time_list = reversed(sorted(set(ip_dic.values())))
	ip_sort_file = open('ip_sorted.txt','wb')

	for time in time_list:
		for key,value in ip_dic.items():
           		if int(value) == int(time):
					print "%s:%s"%(key,value)
                	ip_sort_file.write("%s %s\r\n"%(value,key))
                	ip_wiget_list.append({key:int(value)})

	ip_sort_file.close()
	pickle.dump(ip_wiget_list,open('ip_sorted.pik','wb'))
	pickle.dump(total,open('counts.pik','wb'))

	return ip_wiget_list,total

def global_isp_sts(ISP_DIST,COUNT):
	print u'\t运营商统计(全国)：'
	for isp,stats in ISP_DIST.items():
		ips = len(stats)
		print "%s:%.2f"%(isp.encode('utf-8'),ips/int(COUNT))

def global_region_sts(REGION_DICT,COUNT):
	print u'\t地区分布（全国）：'
	for regions,stats in REGION_DICT.items():
		ips = len(stats)
		print "%s:%.2f"%(regions.encode('utf-8'),ips/int(COUNT))

def region_city_sts(REGION,CITY_DICT):
	city_dic = {}
	# Example = {'xiamen':[ip1,ip2,ip3]}
	isp_dic = {}
	# Example = {'dianxin':[ip1,ip2,ip3]}
	times = len(CITY_DICT)

	for ip,data_list in CITY_DICT.items():
		city = data_list[1]
		isp = data_list[4]
		if city not in city_dic.keys():
			city_dic[city] = []
		city_dic[city].append(ip)
		if isp not in isp_dic.keys():
			isp_dic[isp] = []
		isp_dic[isp].append(ip)

	print u"\t\t%s 分布："%REGION
	for city,ips in city_dic.items():
		print "%s:%4.2f%%"%(city.encode('utf-8'),len(ips)/times*100)

	print u'\t\t%s 运营商统计：'%REGION
	for key,value in isp_dic.items():
		print "%s:%4.2f%%"%(key.encode('utf-8'),len(value)/times*100)
	

if __name__ == '__main__':

	if len(sys.argv) >= 2:
		ip_wiget_list,count = ip_sort(sys.argv[1])
	else:
		ip_wiget_list = pickle.load(open('ip_sorted.pik','r'))
		count = pickle.load(open('counts.pik','r'))

	if not os.path.exists('region_dic.pik') or not os.path.exists('isp_dic.pik'):
		for ip_wight in ip_wiget_list:
			ip = ip_wight.items()[0][0]
			wight = ip_wight.items()[0][1]
			try:
				get_data(ip,wight)
			except Exception as e:
				print e
				continue
			print wight,":",ip
			time.sleep(0.5)
		pickle.dump(region_dic,open('region_dic.pik','wb'))
		pickle.dump(isp_dic,open('isp_dic.pik','wb'))
	else:
		region_dic = pickle.load(open('region_dic.pik','r'))
		isp_dic = pickle.load(open('isp_dic.pik','r'))


	print u'\t合计：(%s个IP)'%count
	global_isp_sts(isp_dic,count)
	global_region_sts(region_dic,count)

	print "####################################################"

	tmp_choices_dic = {}
	choice_str = ''

	for key,value in enumerate(region_dic,1):
		choice_str += '%s.%s\t'%(key,value)
		tmp_choices_dic[str(key)] = value

	print choice_str

	while True:
		choice = raw_input( '选择要详细信息的省份(or exit)：')
		if choice in ("exit","quit","q"):
			break
		try:
			region = tmp_choices_dic[choice]
			print region
			region_city_sts(region,region_dic[region])
		except Exception as e:
			print e 
			continue
