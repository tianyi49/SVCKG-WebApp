from applications.view.toolkit.pre_load import neo4jconn
import pandas as pd
import datetime
from collections import Counter
#将字典转换为Echart的data的格式
def dict2Edata(dictimpacttype={}):
	list=[];dict={}
	for key in dictimpacttype:
		list.append({'value':dictimpacttype[key] , 'name':key})
	dict['data']=list
	return dict
def get_num_by_date(time_date_list,start_time,end_time,item_name):
	count=0;
	s1 = datetime.datetime.strptime(start_time, "%Y-%m-%d")
	s2 = datetime.datetime.strptime(end_time, "%Y-%m-%d")
	for time_date in time_date_list:
		time_date[item_name]=datetime.datetime.strptime(time_date[item_name], "%Y-%m-%d")
		if(time_date[item_name]>=s1 and  time_date[item_name]<=s2):
			count+=1;
	return count
def search_statistical(start_time,end_time,statistic_type):
	# #程序运行时间测试
	# s = datetime.datetime.now()
	db = neo4jconn
	s1 = datetime.datetime.strptime(start_time, "%Y-%m-%d")
	s2 = datetime.datetime.strptime(end_time, "%Y-%m-%d")
	if(s1<=s2):
		if(statistic_type==1 ):
			dictimpacttype= {'硬件':'','操作系统':'','软件':''}
			dictimpacttype['硬件']=db.graph.run('MATCH (n4:published_date)<-[r4:has_date]-(n3:cve_id)-[r3:impact_product]->(n:product)-[r1:has_type]->(n1:product_type) WHERE n1.name="hardware" and date(n4.name) >= date("%s") and date("%s")>= date(n4.name) return count(distinct n3)'%(start_time,end_time)).data()[0]['count(distinct n3)']
			dictimpacttype['操作系统'] = db.graph.run(
				'MATCH (n4:published_date)<-[r4:has_date]-(n3:cve_id)-[r3:impact_product]->(n:product)-[r1:has_type]->(n1:product_type) WHERE n1.name="operatingsystem" and date(n4.name) >= date("%s") and date("%s")>= date(n4.name) return count(distinct n3)' % (
				start_time, end_time)).data()[0]['count(distinct n3)']
			dictimpacttype['软件'] = db.graph.run(
				'MATCH (n4:published_date)<-[r4:has_date]-(n3:cve_id)-[r3:impact_product]->(n:product)-[r1:has_type]->(n1:product_type) WHERE n1.name="software" and date(n4.name) >= date("%s") and date("%s")>= date(n4.name) return count(distinct n3)' % (
				start_time, end_time)).data()[0]['count(distinct n3)']
			dictimpacttype=dict2Edata(dictimpacttype)
			# s = datetime.datetime.now()
			# dictimpacttype['相邻网络'] =db.graph.run(
			# 	'MATCH (n4:published_date)<-[r4:has_date]-(n3:cve_id)-[r3:has_vector]->(n2:attack_vector)-[r2:has_version]->(n1:cvss_version) WHERE n2.name="ADJACENT_NETWORK" and n1.name<>"2.0"return distinct n3.name,n4.name').data()
			# dictimpacttype['远程网络'] =db.graph.run(
			# 	'MATCH (n4:published_date)<-[r4:has_date]-(n3:cve_id)-[r3:has_vector]->(n2:attack_vector)-[r2:has_version]->(n1:cvss_version) WHERE n2.name="NETWORK" and n1.name<>"2.0" return distinct n3.name,n4.name').data()
			# dictimpacttype['本地读写'] =db.graph.run(
			# 	'MATCH (n4:published_date)<-[r4:has_date]-(n3:cve_id)-[r3:has_vector]->(n2:attack_vector)-[r2:has_version]->(n1:cvss_version) WHERE n2.name="LOCAL" and n1.name<>"2.0" return distinct n3.name,n4.name').data()
			# dictimpacttype['物理接触'] =db.graph.run(
			# 	'MATCH (n4:published_date)<-[r4:has_date]-(n3:cve_id)-[r3:has_vector]->(n2:attack_vector)-[r2:has_version]->(n1:cvss_version) WHERE n2.name="PHYSICAL" and n1.name<>"2.0"  return distinct n3.name,n4.name').data()
			# dictimpacttype['网络'] =db.graph.run(
			# 	'MATCH (n4:published_date)<-[r4:has_date]-(n3:cve_id)-[r3:has_vector]->(n2:attack_vector) WHERE (n2.name="NETWORK" or n2.name="ADJACENT_NETWORK" ) return distinct n3.name,n4.name').data()
			# dictimpacttype['本地'] =db.graph.run(
			# 	'MATCH (n4:published_date)<-[r4:has_date]-(n3:cve_id)-[r3:has_vector]->(n2:attack_vector) WHERE (n2.name="LOCAL" or n2.name="PHYSICAL" ) return distinct n3.name,n4.name').data()
			#
			# dictimpacttype['未分类']=db.graph.run(
			# 	'MATCH (n4:published_date)<-[r4:has_date]-(n3:cve_id) return distinct n3.name,n4.name').data()
			# e = datetime.datetime.now()
			# for key in dictimpacttype:
			# 	dictimpacttype[key]=get_num_by_date(dictimpacttype[key],start_time,end_time,'n4.name')
			# print("*********************************程序运行时间", e - s)  # 26.5s

		elif (statistic_type == 2):
			dictimpacttype = {'网络': '', '本地': '', '物理接触': '', '本地读写': '', '相邻网络': '', '远程网络': '', '未分类': ''}
			dictimpacttype['相邻网络'] = db.graph.run(
				'MATCH (n4:published_date)<-[r4:has_date]-(n3:cve_id)-[r3:has_vector]->(n2:attack_vector)-[r2:has_version]->(n1:cvss_version) WHERE n2.name="ADJACENT_NETWORK" and n1.name<>"2.0" and date(n4.name) >= date("%s") and date("%s")>= date(n4.name) return count(distinct n3)' % (
					start_time, end_time)).data()[0]['count(distinct n3)']
			dictimpacttype['远程网络'] = db.graph.run(
				'MATCH (n4:published_date)<-[r4:has_date]-(n3:cve_id)-[r3:has_vector]->(n2:attack_vector)-[r2:has_version]->(n1:cvss_version) WHERE n2.name="NETWORK" and n1.name<>"2.0" and date(n4.name) >= date("%s") and date("%s")>= date(n4.name) return count(distinct n3)' % (
					start_time, end_time)).data()[0]['count(distinct n3)']
			dictimpacttype['本地读写'] = db.graph.run(
				'MATCH (n4:published_date)<-[r4:has_date]-(n3:cve_id)-[r3:has_vector]->(n2:attack_vector)-[r2:has_version]->(n1:cvss_version) WHERE n2.name="LOCAL" and n1.name<>"2.0" and date(n4.name) >= date("%s") and date("%s")>= date(n4.name) return count(distinct n3)' % (
					start_time, end_time)).data()[0]['count(distinct n3)']
			dictimpacttype['物理接触'] = db.graph.run(
				'MATCH (n4:published_date)<-[r4:has_date]-(n3:cve_id)-[r3:has_vector]->(n2:attack_vector)-[r2:has_version]->(n1:cvss_version) WHERE n2.name="PHYSICAL" and n1.name<>"2.0" and date(n4.name) >= date("%s") and date("%s")>= date(n4.name) return count(distinct n3)' % (
					start_time, end_time)).data()[0]['count(distinct n3)']
			dictimpacttype['网络'] = db.graph.run(
				'MATCH (n4:published_date)<-[r4:has_date]-(n3:cve_id)-[r3:has_vector]->(n2:attack_vector) WHERE (n2.name="NETWORK" or n2.name="ADJACENT_NETWORK") and date(n4.name) >= date("%s") and date("%s")>= date(n4.name) return count(distinct n3)' % (
					start_time, end_time)).data()[0]['count(distinct n3)']
			dictimpacttype['本地'] = db.graph.run(
				'MATCH (n4:published_date)<-[r4:has_date]-(n3:cve_id)-[r3:has_vector]->(n2:attack_vector) WHERE (n2.name="LOCAL" or n2.name="PHYSICAL" )  and date(n4.name) >= date("%s") and date("%s")>= date(n4.name) return count(distinct n3)' % (
					start_time, end_time)).data()[0]['count(distinct n3)']

			dictimpacttype['未分类'] = db.graph.run(
				'MATCH (n4:published_date)<-[r4:has_date]-(n3:cve_id) WHERE  date(n4.name) >= date("%s") and date("%s")>= date(n4.name) return count(distinct n3)' % (
					start_time, end_time)).data()[0]['count(distinct n3)'] - dictimpacttype['网络'] - dictimpacttype['本地']
			dictimpacttype['网络未分类'] = dictimpacttype['网络'] - dictimpacttype['远程网络'] - dictimpacttype['相邻网络']
			dictimpacttype['本地未分类'] = dictimpacttype['本地'] - dictimpacttype['本地读写'] - dictimpacttype['物理接触']
		elif (statistic_type == 3):
			dictimpacttype = {'高危': '', '中危': '', '低危': '','未分类':''}
			severitylist= db.graph.run('MATCH (n4:published_date)<-[r4:has_date]-(n3:cve_id)-[r3:has_impact]->(n2:severity) WHERE  date(n4.name) >= date("%s") and date("%s")>= date(n4.name) return n2.name' % (start_time, end_time) ).data()
			dictimpacttype['未分类']= db.graph.run(
				'MATCH (n4:published_date)<-[r4:has_date]-(n3:cve_id) WHERE  date(n4.name) >= date("%s") and date("%s")>= date(n4.name) return count(n3.name)' % (
				start_time, end_time)).data()[0]['count(n3.name)'] -len(severitylist)
			severitylist=[i['n2.name'] for i in severitylist]
			severitydict=Counter(severitylist)
			dictimpacttype['高危']=severitydict['HIGH']+severitydict['CRITICAL']
			dictimpacttype['低危'] = severitydict['LOW']
			dictimpacttype['中危'] = severitydict['MEDIUM']
			dictimpacttype = dict2Edata(dictimpacttype)
		elif (statistic_type == 4):
			dictimpacttype = {'0-2': 0, '2-4': 0, '4-6': 0,'6-8': 0,'8-10': 0,'未评分':''}
			totalnum=db.graph.run('MATCH (n4:published_date)<-[r4:has_date]-(n3:cve_id) WHERE  date(n4.name) >= date("%s") and date("%s")>= date(n4.name) return count(n3.name)'%(start_time, end_time)).data()[0]['count(n3.name)']
			scorelist=db.graph.run('MATCH(n4:published_date)<-[r4:has_date]-(n3:cve_id)-[r3:has_evaluescore]->(n2:cvss_score) WHERE  date(n4.name) >= date("%s") and date("%s")>= date(n4.name) return n2.name' %(start_time, end_time)).data()
			scorelist = [i['n2.name'] for i in scorelist]
			dictimpacttype['未评分']=totalnum-len(scorelist)
			for item in scorelist:
				if(item>=8):
					dictimpacttype['8-10']+=1
				elif(item<2):
					dictimpacttype['0-2'] += 1
				elif(item>=2 and item<4):
					dictimpacttype['2-4'] += 1
				elif(item>=4 and item<6):
					dictimpacttype['4-6'] += 1
				else:
					dictimpacttype['6-8'] += 1
			dictimpacttype=dict2Edata(dictimpacttype)
		#漏洞数量分布
		elif (statistic_type>=10 and statistic_type<=13):
			dictimpacttype={'date':[],'value':[]}
			start_time_pd=start_time.replace('-','')
			end_time_pd=end_time.replace('-','')
			month_list= pd.date_range(start=start_time_pd, end=end_time_pd, freq='M').date.tolist()
			#输入的时间段的月份列表（包含起始时间和结束时间）
			month_xlist=[(str(i).split('-')[0]+'-'+str(i).split('-')[1]) for i in month_list]+[end_time.split('-')[0]+'-'+end_time.split('-')[1]]
			dictimpacttype['date']=month_xlist[:]
			dictimpacttype['value']=[0]*len(month_xlist)
			if(statistic_type==10):
				cveid_datelist = db.graph.run(
					'MATCH (n4:published_date)<-[r4:has_date]-(n3:cve_id)-[r3:has_impact]->(n2:severity) WHERE  date(n4.name) >= date("%s") and date("%s")>= date(n4.name) return distinct n3.name,n4.name' % (start_time, end_time)).data()
			elif (statistic_type == 11):
				cveid_datelist = db.graph.run(
					'MATCH (n4:published_date)<-[r4:has_date]-(n3:cve_id)-[r3:has_impact]->(n2:severity) WHERE (n2.name="HIGH" or n2.name="	CRITICAL") and date(n4.name) >= date("%s") and date("%s")>= date(n4.name) return distinct n3.name,n4.name' % (start_time, end_time)).data()
			elif (statistic_type == 12):
				cveid_datelist = db.graph.run(
					'MATCH (n4:published_date)<-[r4:has_date]-(n3:cve_id)-[r3:has_impact]->(n2:severity{name:"MEDIUM"}) WHERE  date(n4.name) >= date("%s") and date("%s")>= date(n4.name) return distinct n3.name,n4.name' % (start_time, end_time)).data()
			elif (statistic_type == 13):
				cveid_datelist=db.graph.run('MATCH (n4:published_date)<-[r4:has_date]-(n3:cve_id)-[r3:has_impact]->(n2:severity{name:"LOW"}) WHERE  date(n4.name) >= date("%s") and date("%s")>= date(n4.name) return distinct n3.name,n4.name' % (start_time, end_time)).data()
			#对每个月的漏洞数量进行统计
			for cveid_date in cveid_datelist:
				cveid_date['n4.name']=cveid_date['n4.name'].rsplit('-',1)[0]
				for i in range(len(month_xlist)):
					if(month_xlist[i]==cveid_date['n4.name']):
						dictimpacttype['value'][i]+=1
						break;
		else:
			dictimpacttype={}
		# e = datetime.datetime.now()
		# print("*********************************程序运行时间", e - s)  # 26.5s
	else:
		dictimpacttype = {}
	return dictimpacttype
