#!/usr/bin/env python
#-*-coding:utf-8-*-

#处理任务log的类，可以获取新的task，改变制定行task的状态码，封装一个task数据包
# 这里是下载图像库的task，每一个task定义为全部下载一个3级view下的所有图片
#task数据包的格式，相对与database的路径；状态码；所属编号
from FileRobotClass import FileRobot
import os,sys,codecs
import re

FRobot=FileRobot()
line_num_store=1
# database_path=FRobot.get_deep_folder_path(home_path,'database')
# log_path=FRobot.get_deep_folder_path(home_path,'LogFile')

num2text={2:'a植物',3:'b植物',4:'c植物',5:'d植物'}
class TaskLog():
	def __init__(self,input_log_path='',input_database_path=''):
		self.log_path=input_log_path
		self.database_path=input_database_path
		self.home_path=sys.path[0] #当前路径
		pass

	# 读取总日志，注意调试时file_read用完一次要关闭，否则它会继续原来的地方读取
	def read_plan_log(self,line_ind):
		file_read = codecs.open(self.log_path + '\PlanLog.txt','r','utf-8')
		log_line = file_read.readlines()[line_ind - 1]
		task_dic = {'URL': '', 'Text': ''}
		task_dic['statecode'] = int(log_line.split('statecode')[1])
		task_dic['URL'] = log_line.split('#')[0]
		task_dic['ind'] = int(log_line.split('@')[1])
		task_dic['Text'] = log_line.split('@')[0].split('#')[1]
		task_dic['p']=log_line.split('p=')[1][0]
		task_dic['m'] = int(log_line.split('m=')[1][0])
		task_dic['m_text'] = num2text[task_dic['m']]
		task_dic['path']=self.database_path+'\\'+task_dic['m_text']+'\\'+task_dic['p']
		file_read.close()
		return task_dic

	#设置指定行状态码
	def set_log(self,log_name,line,statecode):
		file_read = codecs.open(self.log_path + '/'+log_name+'.txt','r','utf-8')
		log_text = file_read.read()
		file_read.close()
		# new_log_text=log_text.replace('@'+str(line)+'@statecode'+'/d','@'+str(line)+'@statecode'+str(statecode))
		old_str='@'+str(line)+'@statecode\d'
		new_str='@'+str(line)+'@statecode'+str(statecode)
		new_log_text=re.sub(old_str,new_str,log_text)
		file_read = codecs.open(self.log_path + '/'+log_name+'.txt', 'w','utf-8')
		file_read.write(new_log_text)
		file_read.close()
		return

	def parse_task_log(self,log_name,line_ind,input_father_ind):#解析task日志指定行,返回一个task（三级目录）
		file_read = codecs.open(self.log_path + '/'+log_name+'.txt','r','utf-8')
		try:
			task_log_line = file_read.readlines()[line_ind - 1]
			task_dic = {'path': ''}
			task_dic['path']=task_log_line.split('\database')[1].split('statecode')[0].split('@')[0]
			task_dic['statecode']=int(task_log_line.split('statecode')[1])
			task_dic['father_ind']=input_father_ind
			task_dic['ind']=task_log_line.split('\database')[1].split('statecode')[0].split('@')[1]
			return task_dic
		except:#如果超出范围，就返回None
			return None

	def set_task_state(self,task_dic):#收到客户端的task之后，返回根据数据设定log，注意为dic
		log_name = self.get_logname_by_Index(task_dic['father_ind'])
		self.set_log(log_name,int(task_dic['ind']),int(task_dic['statecode']))
		return

	def get_new_task_byFatherInd(self,input_father_ind):#给定总log中的行号，返回一个task或者完成标志
		log_name=self.get_logname_by_Index(input_father_ind)
		line_ind = 1
		while True:
			task_dic = self.parse_task_log(log_name,line_ind,input_father_ind)
			if task_dic==None:
				return task_dic
			elif task_dic['statecode']==3:
				self.set_log(log_name,line_ind,2)
				break
			line_ind += 1
		return task_dic#可能是找到了，也可能是None

	def get_new_task(self,line_ind = 1): #状态码1完成 3未完成 2正在完成;所以找的是2,3
		while True:
			if self.read_plan_log(line_ind)['statecode']!=1:
				break
			line_ind += 1
			if line_ind==85:
				return None
		if self.read_plan_log(line_ind)['statecode']==3:#已下载，但未完成
			self.set_log('PlanLog',line_ind, 2)  # 设置为正在处理状态码
		#到此为止，拿到的line_ind的状态必定为2
		task_dic=self.get_new_task_byFatherInd(line_ind)
		if task_dic==None:
			self.set_log('PlanLog', line_ind, 1)  # 设置为处理完毕
			return self.get_new_task(line_ind=line_ind+1)
		else:
			return task_dic

	def get_logname_by_Index(self,line_num):  # 根据行号，获取该行对应的log名字
		task_dic = self.read_plan_log(line_num)
		return task_dic['Text']

	def is_level_3(self,folder_path):

		try:
			message_text = FRobot.read_message(folder_path, 'index_message')
			if '#3#' in message_text:
				return True
			else:
				return False
		except :
			return False

	# 找出文件夹下所有3级的文件夹,task写入log
	def find_LV3_folder(self,root_path, log_name):

		filelist, dirslist = FRobot.get_folder_file_list(root_path)  # 遍历第一级文件夹
		if len(dirslist) > 0:  # 存在子文件夹
			if len(dirslist) > 0 and 'index_message.txt' in filelist:  # 是否存在index_message？是否包含文件夹？
				if self.is_level_3(root_path):  # 是否是LV3？
					file_read = codecs.open(self.log_path + '\\' + log_name + '.txt', 'r','utf-8')
					line_num = len(file_read.readlines())+1
					file_read.close()
					FRobot.write_text(self.log_path, log_name, root_path+'@'+str(line_num)+'@statecode3', style_flag=3)#状态码1完成 3未完成 2正在完成
					return
			for dir in dirslist:
				new_root_path = FRobot.get_deep_folder_path(root_path, dir)
				self.find_LV3_folder(new_root_path, log_name)


	# 找出文件夹下所有3级的文件夹,task写入log
	def find_LV3_folder_v2(self,root_path, log_name):
		filelist, dirslist = FRobot.get_folder_file_list(root_path)  # 遍历第一级文件夹
		if len(dirslist) > 0:  # 存在子文件夹
			# print(filelist)
			if 'index_message.txt' in filelist:
				# print(root_path)
				if self.is_level_3(root_path):
					file_read = codecs.open(self.log_path + '\\' + log_name + '.txt', 'r','utf-8')
					line_num = len(file_read.readlines())+1
					file_read.close()
					FRobot.write_text(self.log_path, log_name, root_path+'@'+str(line_num)+'@statecode3', style_flag=3)
				else:
					for dir in dirslist:
						new_root_path = FRobot.get_deep_folder_path(root_path, dir)
						self.find_LV3_folder_v2(new_root_path, log_name)	
			else:
				for dir in dirslist:
					new_root_path = FRobot.get_deep_folder_path(root_path, dir)
					self.find_LV3_folder_v2(new_root_path, log_name)						














