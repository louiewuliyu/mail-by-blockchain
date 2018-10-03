#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from email import encoders
from email.header import Header, decode_header
from email.parser import Parser
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
#smtp, pop3協議
import smtplib
import poplib
#block chain
import hashlib
import datetime
import time

class send_email(object):
	"""docstring for send_email"""
	def __init__(self, from_addr, password, to_addr, smtp_server):
		super(send_email, self).__init__()
		self.from_addr = from_addr
		self.password = password
		self.to_addr = to_addr
		self.smtp_server = smtp_server
		self.msg = None

	def _format_addr(self, s):
	    name, addr = parseaddr(s)
	    return formataddr((Header(name, 'utf-8').encode(), addr))

	def create_message(self, message):
		"""Type --> Text"""
		self.msg = MIMEText(message, 'plain', 'utf-8')
		self.msg['From'] = self._format_addr('Python <%s>' % self.from_addr)
		self.msg['To'] = self._format_addr('管理員 <%s>' % self.to_addr)
		self.msg['Subject'] = Header('Email track testing', 'utf-8').encode()

	def connect(self):
		"""email sending"""
		server = smtplib.SMTP()
		server.connect(self.smtp_server, 587)
		server.starttls()
		server.set_debuglevel(1)
		server.login(self.from_addr, self.password)
		server.sendmail(self.from_addr, [self.to_addr], self.msg.as_string())
		print('------success------')
		server.quit()

class fetch_email(object):
	"""docstring for fetch_email"""
	def __init__(self, email, password, pop3_server):
		super(fetch_email, self).__init__()
		self.email = email
		self.password = password
		self.pop3_server = pop3_server
		self.msg = None
		self.block_message = []

	def decode_str(self, s):
	    value, charset = decode_header(s)[0]
	    if charset:
	        value = value.decode(charset)
	    return value

	def guess_charset(self, m):
	    charset = m.get_charset()
	    if charset is None:
	        content_type = m.get('Content-Type', '').lower()
	        pos = content_type.find('charset=')
	        if pos >= 0:
	            charset = content_type[pos + 8:].strip()
	    return charset

	def print_info(self, temp_msg, indent=0):
	    text_result = None
	    if indent == 0:
	        for header in ['From', 'To', 'Subject']:
	            value = temp_msg.get(header, '')
	            if value:
	                if header=='Subject':
	                    value = self.decode_str(value)
	                else:
	                    hdr, addr = parseaddr(value)
	                    name = self.decode_str(hdr)
	                    value = u'%s <%s>' % (name, addr)
	            print('%s%s: %s' % ('  ' * indent, header, value))
	    if (temp_msg.is_multipart()):
	        parts = temp_msg.get_payload()
	        for n, part in enumerate(parts):
	            print('%spart %s' % ('  ' * indent, n))
	            print('%s--------------------' % ('  ' * indent))
	            self.print_info(part, indent + 1)
	    else:
	        content_type = temp_msg.get_content_type()
	        if content_type=='text/plain' or content_type=='text/html':
	            content = temp_msg.get_payload(decode=True)
	            charset = self.guess_charset(temp_msg)
	            if charset:
	                content = content.decode(charset)
	            print('%sText: %s' % ('  ' * indent, content + '...'))
	        else:
	            print('%sAttachment: %s' % ('  ' * indent, content_type))

	def content(self, temp_msg, temp_content):
	    for par in temp_msg.walk():
	        if not par.is_multipart(): # 这里要判断是否是multipart，是的话，里面的数据是一个message 列表
	            name = par.get_param('name')
	            if name:    #有附件
	                file_name = decode_str(name)
	                print('File name: ', file_name)
	                data = par.get_payload(decode = True)   #　解码出附件数据，然后存储到文件中
	                temp_content.append(data)
	            else:
	                temp = par.get_payload(decode = True)
	                charset = self.guess_charset(par)
	                if charset:
	                    temp = temp.decode(charset)
	                temp_content.append(temp)
	            temp_content.append('\n\t')	#split the data

	def decode_email(self):
		if not self.msg:
			return 'No msg'
		#self.print_info(self.msg)
		subject = self.msg.get('subject')
		subject = self.decode_str(subject)
		temp_content = []	#存儲郵件內容
		self.content(self.msg, temp_content)
		print('\n%s' % ('-'*60))
		print('----Subject: ', subject)
		print('----From: ', parseaddr(self.msg.get('from'))[1])
		print('----Date: ', self.msg.get('date'))
		print('----MessagesID: ', parseaddr(self.msg.get('message-id'))[1])
		print('----Content: ', temp_content)
		print('%s' % ('-'*60))
		self.block_message = [subject, parseaddr(self.msg.get('from'))[1], self.msg.get('date'), parseaddr(self.msg.get('message-id'))[1], temp_content]

	def connect(self):
		#server = poplib.POP3_SSL('pop.googlemail.com', '995')	#連接到pop3_server
		#server.set_debuglevel(1)	#可以打開或關閉調適信息
		server = poplib.POP3_SSL(self.pop3_server, '995')	#連接到pop3_server
		server.set_debuglevel(1)	#可以打開或關閉調適信息
		print(server.getwelcome().decode('utf-8'))	#連入pop3_server提醒
		#身分認證
		server.user(self.email)
		server.pass_(self.password)
		#返回郵箱內狀態
		print('Messages: %s. Size: %s' % server.stat())

		resp, mails, octets = server.list()	#list()返回所有郵件的編號
		#print(mail) --> [b'1 82923', b'2 2184', ...]
		index = len(mails)
		resp, lines, octets = server.retr(index)	#取最近的一封郵件
		msg_content = b'\r\n'.join(lines).decode('utf-8')	#lines存儲郵件的原始文本的每一行，獲得整個原始文本

		#解析郵件
		self.msg = Parser().parsestr(msg_content)

		