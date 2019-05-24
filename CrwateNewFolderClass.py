#!/usr/bin/env python
#-*-coding:utf-8-*-

#创建新的目录
import threading
import math
import time,os,sys,shutil 
from FileRobotClass import FileRobot
from TaskLogClass import TaskLog


home_path=sys.path[0] #当前路径

class CrwateNewFolder():
	def __init__(self,input_new_path):
		super(CrwateNewFolder, self).__init__()
		self.new_path=input_new_path
		self.FRobot=FileRobot()
		self.new_main_path=self.FRobot.get_deep_folder_path(self.new_path,'main')
		self.new_mini_path=self.FRobot.get_deep_folder_path(self.new_path,'mini')
		if not os.path.exists(self.new_main_path):
			self.FRobot.creat_folder(self.new_path,'main')
		if not os.path.exists(self.new_mini_path):
			self.FRobot.creat_folder(self.new_path,'mini')	
		self.database_path=self.FRobot.get_deep_folder_path(home_path,'database')
		self.log_path=self.FRobot.get_deep_folder_path(home_path,'LogFile')
		self.TLog=TaskLog(input_log_path=self.log_path,input_database_path=self.database_path)

	def get_pic_num(self,input_path):
		filelist,dirslist = self.FRobot.get_folder_file_list(input_path)
		num=0
		for file in filelist:
			if '.jpg' in file:
				num+=1
		return num			
	
	def get_name(self,input_path):
		try:
			text=self.FRobot.read_message(input_path,'index_message')
			return text.split('#')[1],text.split('#')[0]
		except :
			print('读取index_message失败')
			return 'en','cn'
			raise

	def move_pic(self,input_path):
		pic_num=self.get_pic_num(input_path)
		en_name,cn_name=self.get_name(input_path)
		main_num=math.ceil(pic_num*0.75)
		mini_num=pic_num-main_num
		print(input_path+'有'+str(pic_num)+'副图片,英文名字为'+en_name+'中文名字为'+cn_name+' main库里有'+str(main_num)+' mini库里有'+str(mini_num))
		pic_folder_name=en_name
		new_pic_main_path=self.FRobot.creat_folder(self.new_main_path,pic_folder_name)
		new_pic_mini_path=self.FRobot.creat_folder(self.new_mini_path,pic_folder_name)
		filelist,dirslist = self.FRobot.get_folder_file_list(input_path)
		main_count=0#计算有多少个被复制进了main
		direction_Path=new_pic_main_path
		for file in filelist:
			if '.jpg' in file:
				shutil.copyfile(input_path+'\\'+file,direction_Path+'\\'+file)
				if mini_num==0:
					shutil.copyfile(input_path+'\\'+file,new_pic_mini_path+'\\'+file)
				main_count+=1
				if main_count>=main_num:
					direction_Path=new_pic_mini_path
					pass
				pass
			pass
		pass

	def process(self,input_path):#遍历文件夹下所有路径
		if self.TLog.is_LV3_with_pic(input_path):#是3级目录，而且有图片，处理
			self.move_pic(input_path)
			pass
		else:
			filelist,dirslist = self.FRobot.get_folder_file_list(input_path)
			if len(dirslist)>0:
				for dir in dirslist:
					dir_path = self.FRobot.get_deep_folder_path(input_path,dir)
					self.process(dir_path)
				pass
