#!/usr/bin/env python
#-*-coding:utf-8-*-

import socket
import threading
import time,sys,os
from TaskLogClass import TaskLog
from FileRobotClass import FileRobot

server_IP='127.0.1.1' #服务器IP
server_Port=2725  #客户端
MAX_connect=300 #最大连接数
wait_timeout_num=5 #连接时等待多少次
wait_timeout=1 #连接时每次等待多少秒
client_inputIP_timeout=3 #客户端没有与服务器建立相应的话，多久后重新输入IP
server_conform_message=b'ConnectSuccess?'#连接建立后服务器发送的确认信息
client_conform_message=b'YesSuccess'#连接建立后客户端确认
client_ask_task_message=b'SendTaskPlease'#请求task
client_send_task_result_message=b'TaskProcessOver'#发送一个task处理结果

task_none=b'NoTask'#没有task了
environment_flag=1 #1本地 2打包后的地址

if environment_flag==1:
	home_path=sys.path[0] #当前路径
else:
	now_path=sys.path[0]
	home_path=now_path.split('\dist')[0]

FRobot=FileRobot()
database_path=FRobot.get_deep_folder_path(home_path,'database')
log_path=home_path+'/LogFile'
TLog=TaskLog(input_log_path=log_path,input_database_path=database_path)

class TCP():
	def __init__(self, input_TCPtype,input_server_IP=server_IP):
		self.TCPtype=input_TCPtype #1客户端 2服务器
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.hostname=socket.gethostname() #主机名称
		if self.TCPtype==2:
			# self.Local_IP = '172.17.228.44'
			self.Local_IP = socket.gethostbyname(self.hostname) #自身IP，对于服务器端就是TCP网络的控制中心IP
				
		else:
			self.client_task=''
			self.Local_IP = input_server_IP #这里如果不制定的话，设定为默认值

	def client_start(self,work_mode=1,send_task=''):#work_mode为1时，请求一个task；2时发送一个task
		if os.path.exists(log_path+'\\IP_address.txt'):
			self.Local_IP=FRobot.read_message(log_path,'IP_address')
			pass
		try:
			self.socket.settimeout(client_inputIP_timeout)
			self.socket.connect((self.Local_IP, server_Port))  # 建立连接:

			# self.socket.connect(('tcp://ittun.com', 53170))  # 建立连接:


		except:
			self.socket.close()
			self.Local_IP=input(str(client_inputIP_timeout)+'秒内没有与服务器建立连接，请输入控制中心IP：\n')
			print('输入的IP是'+self.Local_IP) #接下来，一切重新开始
			FRobot.write_text(log_path,'IP_address',self.Local_IP,style_flag=1)
			self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.socket.settimeout(client_inputIP_timeout*10)
			self.socket.connect((self.Local_IP, server_Port))  # 再次建立连接:
		finally:
			for i in range(1,wait_timeout_num):
				receive_conform_message = self.socket.recv(2048).decode('utf-8')  # 接收确认信息
				if receive_conform_message == server_conform_message.decode('utf-8'):
					self.socket.send(client_conform_message)  # 发送返回确认
					time.sleep(wait_timeout)
					print('与服务器互相确认完毕，正式开始收发信息')
					#下面为真正的传递信息
					if work_mode==1:
						self.client_task = eval(self.client_ask_task()) #字符串转换成字典
					else:
						self.client_send_task_result(send_task)
						self.client_task = None
					break
				time.sleep(wait_timeout)
			# self.socket.send(b'exit')
			self.socket.close()
			return self.client_task

	#客户端请求一个task
	def client_ask_task(self):
		self.socket.send(client_ask_task_message)  # 请求task
		while True:
			receive_task=self.socket.recv(2048).decode('utf-8')
			if receive_task!=task_none.decode('utf-8'):
				print('收到一个任务：'+receive_task)
				return receive_task
			else:
				return None

	#客户端发送一个task处理结果
	def client_send_task_result(self,task_to_send):
		self.socket.send(client_send_task_result_message)
		time.sleep(wait_timeout)
		print('向服务器报告，完成了任务：'+str(task_to_send))
		self.socket.send(str(task_to_send).encode('utf-8'))

	# 服务器与客户端通讯函数
	def server_communicate(self,sock):
		while True:
			receive_message=sock.recv(2048).decode('utf-8')
			if receive_message==client_ask_task_message.decode('utf-8'):  # 发现客户端是想请求task
				new_task_str = str(TLog.get_new_task())
				sock.send(new_task_str.encode('utf-8'))
				return
			elif receive_message==client_send_task_result_message.decode('utf-8'):  # 发现客户端是发送task
				receive_task_result_message_str = sock.recv(2048).decode('utf-8') # 接收返回确认信息
				# print(receive_task_result_message_str)
				# print('hhahahahhah')
				receive_task_result_message = eval(receive_task_result_message_str)
				TLog.set_task_state(receive_task_result_message) #根据结果设定
				return

	#服务器端开始监听
	def server_start(self):
		print('服务器端（控制中心）的本地IP是'+self.Local_IP)
		self.socket.bind((self.Local_IP,server_Port))
		self.socket.listen(MAX_connect)
		print('Waiting for connection...')
		while True:
			sock, addr = self.socket.accept()# 接受一个新连接:
			server_thread = threading.Thread(target=self.server_tcplink, args=(sock, addr))# 创建新线程来处理TCP连接:
			server_thread.start()

	#服务器端处理已经建立的连接
	def server_tcplink(self,sock, addr):
		current_thread_name=threading.current_thread().name #当前线程名字
		print('线程'+current_thread_name+'接受了一个新连接，来自客户端： %s:%s' % addr)
		sock.send(server_conform_message)
		for i in range(1,wait_timeout_num):
			receive_conform_message = sock.recv(2048).decode('utf-8')  # 接收返回确认信息
			if receive_conform_message == client_conform_message.decode('utf-8'):
				print('线程'+current_thread_name+'与客户端互相确认完毕，正式开始收发信息')
				#下面是真正的传递信息
				self.server_communicate(sock)
			time.sleep(wait_timeout)
		sock.close()
		print('线程'+current_thread_name+'与客户端连接结束： %s:%s' % addr)