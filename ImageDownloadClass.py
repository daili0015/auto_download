#!/usr/bin/env python
#-*-coding:utf-8-*-

import threading
import time
import os,sys,random
import requests
from TCPClass import TCP
from FileRobotClass import FileRobot
from TaskLogClass import TaskLog


FRobot=FileRobot()
download_timeout=10
pause_time=0.3#成功后停顿的时间
repeat_time=3#失败重试几次
home_path=sys.path[0] #当前路径
database_path=FRobot.get_deep_folder_path(home_path,'database')
log_path=FRobot.get_deep_folder_path(home_path,'LogFile')
UserAgent_List = [
	"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
	"Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
	"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
	"Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
	"Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
	"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
	"Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
	"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
	"Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
	"Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
	"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
	"Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
	"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
	"Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
	"Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
	"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
	"Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
]

class ImageDownload():
	def __init__(self):
		super(ImageDownload, self).__init__()
		self.task=''

	def get_image_header(self,refer_url):#获取随机的header
		return {'User-Agent': random.choice(UserAgent_List),
	             'Accept':"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
	             'Cache-Control': 'no-cache',
	             'Upgrade-Insecure-Requests': '1',
	             'Referer': refer_url
	             }	

	def process_task(self,task,image_limit=10000): #image_limit最多下载数量
		# self.task=task
		level_3_path=database_path+task['path']
		filelist,dirslist=FRobot.get_folder_file_list(level_3_path)
		print(filelist)
		print(dirslist)
		if len(dirslist)==0:
			return
		else:
			current_num=0
			for dir in 	dirslist:
				if current_num>=image_limit:#超输出数量，不再下载
					break
				image_dir_path=FRobot.get_deep_folder_path(level_3_path,dir)#图片的URL
				current_num+=1
				try:
					self.download_image(image_dir_path,size=1)#1原图，2缩略图
				except :
					print('图片下载失败')


#简单的下载图片函数
	def download_image(self,image_location,size=1,repeat=repeat_time): #1原图，2缩略图
		try:
			rod=FRobot.parse_image(image_location)#解析图像下载信息
			print('解析成功')
		except:
			return
		image_save_location=FRobot.get_father_dir(image_location)#保存位置
		image_save_name=FRobot.get_self_name(image_location)#保存位置
		if os.path.exists(image_save_location+'\\'+image_save_name+'.jpg'):
			print('图片已经存在，跳过')
			return
		headers=self.get_image_header(rod['refer_url'])#获取随机的header
		try:
			if size==1:
				image_html = requests.get(rod['image_src'],
				                          headers=headers, timeout=download_timeout)
				f = open(image_save_location+'\\'+image_save_name+'.jpg', 'ab')
			else:
				image_html = requests.get(rod['thumbnail_src'],
				                          headers=headers, timeout=download_timeout)
				f = open(image_save_location+'\\'+image_save_name+'thumb.jpg', 'ab')
				print('下载成功！停顿'+str(pause_time)+'秒')
				time.sleep(pause_time)
		except :
			if repeat>0:
				print('下载失败，停顿一下，再次下载')
				time.sleep(pause_time)
				self.download_image(image_location,size=1,repeat=repeat-1)#1原图，2缩略图
			else:
				print('下载失败，放弃下载')
		print('下载得到图片！保存图片大小为' + str(len(image_html.content)))
		f.write(image_html.content)
		f.close()