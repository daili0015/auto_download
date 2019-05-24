#!/usr/bin/env python
#-*-coding:utf-8-*-

# 客户端
import socket
import threading
import time,os,sys
from TCPClass import TCP
from FileRobotClass import FileRobot
from ImageDownloadClass import ImageDownload

# home_path=sys.path[0] #当前路径
# FRobot=FileRobot()
# database_path=FRobot.get_deep_folder_path(home_path,'database')
image_limit_num=10000 #每个文件夹下几张
thread_num=8#线程数

def thread_fun():
	while True:
		client1=TCP(1)#建立连接，请求任务
		task_dic=client1.client_start(work_mode=1)
		try:
			print('线程'+threading.current_thread().getName()+'请求任务成功！开始下载任务')
			downloader=ImageDownload()#进行下载
			downloader.process_task(task_dic,image_limit=image_limit_num)
			task_dic['statecode']=1
		except :
			task_dic['statecode']=2
		finally:
			client2=TCP(1)
			client2.client_start(work_mode=2,send_task=task_dic)

# 线程相关
threads = []
for i in range(0,thread_num):
	t = threading.Thread(target=thread_fun)
	threads.append(t)
for t in threads:
	time.sleep(0.7)
	t.start()
print(len(threading.enumerate()))