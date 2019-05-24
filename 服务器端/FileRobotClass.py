#!/usr/bin/env python
#-*-coding:utf-8-*-

import  os,codecs
class FileRobot():
	def __init__(self):
		pass

	#返回当前路径下所有文件，文件夹
	def get_folder_file_list(self,input_path):
		for rootpath, dirslist, filelist in os.walk(input_path):
			return  filelist,dirslist

	#给定文件夹目录，给定希望进入的文件夹名字
	def get_deep_folder_path(self,input_path,input_name):
		return input_path+'\\'+input_name

	#文件夹的名字不能含有的特殊符号，windows下的限定
	def get_format_filename(self,input_filename):
		for s in ['?', '*', '<', '>', '\★', '！', '/','!']:
			while s in input_filename:
				input_filename = input_filename.strip().replace(s, '')
		return input_filename

	#给定目录，以给定名字下创建文件夹
	def creat_folder(self,input_location,input_foldername):
		input_foldername=self.get_format_filename(input_foldername)
		if not os.path.exists(input_location+'\\'+input_foldername):
			try:
				os.makedirs(input_location+'\\'+input_foldername)
				return input_location+'\\'+input_foldername
			except:
				return False
		else:
			return input_location+'\\'+input_foldername

	#解析image_message信息
	def parse_image(self,input_file_location):
		message_list=self.read_message(input_file_location,'image_message').split('#')
		message_list[4].replace('/236/','/b/')
		return {'image_name': message_list[0], 'refer_url': message_list[2],
		        'thumbnail_src': message_list[4],'image_src':message_list[4].replace('/236/','/b/')}

	#读取txt文件
	def read_message(self,input_file_location,input_file_name):

		os.chdir(input_file_location)
		file_read = open(input_file_name+'.txt','r')
		try:
			return file_read.read()
		finally:
			file_read.close()

	#获取父文件夹的路径
	def get_father_dir(self,dir):
		return dir[::-1].split('\\', 1)[1][::-1]

	#获取自己文件夹的名字
	def get_self_name(self,dir):
		return dir[::-1].split('\\', 1)[0][::-1]


	#打开txt文件，写入文件;style_flag写入方式，1覆盖写入，2继续写入，3换行继续写入
	def write_text(self,input_file_location,input_file_name,input_text,style_flag=1):
		input_file_name=self.get_format_filename(input_file_name)
		try:
			os.chdir(input_file_location)  # 切换到上面创建的文件夹
			if style_flag==1:
				f = codecs.open(input_file_name + '.txt', 'w','utf-8')  # r只读，w可写，a追加
				f.write(input_text)
				f.close()
			elif style_flag==2:
				f = codecs.open(input_file_name + '.txt', 'a','utf-8')
				f.write(input_text)
				f.close()
			elif style_flag==3:
				f_read=codecs.open(input_file_name + '.txt', 'r','utf-8')
				if len(f_read.read())==0:#如果是空的就不换行了
					self.write_text(input_file_location,input_file_name,input_text,style_flag=1)
				else:
					f = codecs.open(input_file_name + '.txt', 'a','utf-8')
					f.write('\n'+input_text)
					f.close()
				f_read.close()
			return True
		except:
			return False