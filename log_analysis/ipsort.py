#!/usr/bin/env python
#coding:utf-8

ips = open('ips.txt','r')

ips_all = ips.read()

ips_list = ips_all.strip().split('\n')
#print ips_list

ip_dic = {}
for ip in set(ips_list):
	count = ips_list.count(ip)
	ip_dic[ip.strip()] = count


time_list = reversed(sorted(set(ip_dic.values())))

ip_sort = open('ips_sort.txt','wb')

for time in time_list:
	for key,value in ip_dic.items():
		if int(value) == int(time):
			print "%s:%s"%(key,value)
			ip_sort.write("%s %s\r\n"%(value,key))
ip_sort.close()
