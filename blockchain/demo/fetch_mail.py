#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr
import email
import poplib

# 输入邮件地址, 口令和POP3服务器地址:
email = input('Email: ')
password = input('Password: ')
pop3_server = input('POP3 server: ')

def guess_charset(msg):
    charset = msg.get_charset()
    if charset is None:
        content_type = msg.get('Content-Type', '').lower()
        pos = content_type.find('charset=')
        if pos >= 0:
            charset = content_type[pos + 8:].strip()
    return charset

def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value


def decode_email(msg):
    subject = msg.get('subject')
    h = decode_str(subject)
    temp_content = []
    content(msg, temp_content)
    #h = email.Header.Header(subject)
    #dh = email.Header.decode_header(h)
    #subject = dh[0][0]
    print_info(msg)
    print('\n%s' % ('-'*60))
    print('----Subject: ', h)
    print('----From: ', parseaddr(msg.get('from'))[1])
    print('----Date: ', msg.get('date'))
    print('----MessagesID: ', parseaddr(msg.get('message-id'))[1])
    print('----Content: ', temp_content)
    print('%s' % ('-'*60))
    block_message = [h, parseaddr(msg.get('from'))[1], msg.get('date'), parseaddr(msg.get('message-id'))[1], temp_content]

def content(msg, temp_content):
    for par in msg.walk():
        if not par.is_multipart(): # 这里要判断是否是multipart，是的话，里面的数据是一个message 列表
            name = par.get_param('name')
            if name:    #有附件
                file_name = decode_str(name)
                print('File name: ', file_name)
                data = par.get_payload(decode = True)   #　解码出附件数据，然后存储到文件中
                temp_content.append(data)
            else:
                temp = par.get_payload(decode = True)
                charset = guess_charset(par)
                if charset:
                    temp = content.decode(charset)
                temp_content.append(temp)

def print_info(msg, indent=0):
    text_result = None
    if indent == 0:
        for header in ['From', 'To', 'Subject']:
            value = msg.get(header, '')
            if value:
                if header=='Subject':
                    value = decode_str(value)
                else:
                    hdr, addr = parseaddr(value)
                    name = decode_str(hdr)
                    value = u'%s <%s>' % (name, addr)
            print('%s%s: %s' % ('  ' * indent, header, value))
    if (msg.is_multipart()):
        parts = msg.get_payload()
        for n, part in enumerate(parts):
            print('%spart %s' % ('  ' * indent, n))
            print('%s--------------------' % ('  ' * indent))
            print_info(part, indent + 1)
    else:
        content_type = msg.get_content_type()
        if content_type=='text/plain' or content_type=='text/html':
            content = msg.get_payload(decode=True)
            charset = guess_charset(msg)
            if charset:
                content = content.decode(charset)
            print('%sText: %s' % ('  ' * indent, content + '...'))
        else:
            print('%sAttachment: %s' % ('  ' * indent, content_type))

# 连接到POP3服务器:
#server = poplib.POP3(pop3_server)
server = poplib.POP3_SSL('pop.googlemail.com', '995')

# 可以打开或关闭调试信息:
server.set_debuglevel(1)
# 可选:打印POP3服务器的欢迎文字:
print(server.getwelcome().decode('utf-8'))
# 身份认证:
server.user(email)
server.pass_(password)
# stat()返回邮件数量和占用空间:
print('Messages: %s. Size: %s' % server.stat())
# list()返回所有邮件的编号:
resp, mails, octets = server.list()
# 可以查看返回的列表类似[b'1 82923', b'2 2184', ...]
print(mails)
# 获取最新一封邮件, 注意索引号从1开始:
index = len(mails)
resp, lines, octets = server.retr(index)
# lines存储了邮件的原始文本的每一行,
# 可以获得整个邮件的原始文本:
msg_content = b'\r\n'.join(lines).decode('utf-8')
# 稍后解析出邮件:
msg = Parser().parsestr(msg_content)
#print_info(msg)
decode_email(msg)
# 可以根据邮件索引号直接从服务器删除邮件:
# server.dele(index)
# 关闭连接:
server.quit()