#!/usr/bin/env python
#-*-coding:utf-8-*-
import socket
import threading
import time
import os,sys
from TCPClass import TCP
from FileRobotClass import FileRobot
from TaskLogClass import TaskLog

while True:
	try:
		server1=TCP(2)
		server1.server_start()
	except :
		raise
	finally:
		pass


# home_path=sys.path[0] #当前路径
# FRobot=FileRobot()
# database_path=FRobot.get_deep_folder_path(home_path,'database')
# log_path=FRobot.get_deep_folder_path(home_path,'LogFile')
# TLog=TaskLog(input_log_path=log_path,input_database_path=database_path)
# # 创建所有log文件
# for i in range(1,85):
# 	i_log_name=TLog.get_logname_by_Index(i)
# 	FRobot.write_text(log_path,i_log_name,'',style_flag=1)
# # 遍历文件夹,每个task写入log
# p_list=['B','C','D','E','F','G','H','J','K','L','M','N','P','Q','R','S','T','W','X','Y','Z']
# m_dic={'2': '苔藓植物','3': '蕨类植物','4': '裸子植物','5': '被子植物' }
# for m in m_dic:
# 	current_path_m = FRobot.get_deep_folder_path(database_path, m_dic[m])
# 	for p in p_list:
# 		current_path_p=FRobot.get_deep_folder_path(current_path_m,p)
# 		log_name=m_dic[m]+'_'+p
# 		print(log_name)
# 		TLog.find_LV3_folder(current_path_p, log_name)











