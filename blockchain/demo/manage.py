'''-*- coding: utf-8 -*-'''

import email_track
import blockchain
import spam_filter

import poplib
import numpy as nu
import pandas as pd

def send_block():
	user = input('Email user: ')
	password = input('User password: ')
	smtp_server = input('Smtp server: ')
	to_addr = input('User you send: ')
	temp_server = email_track.send_email(user, password, to_addr, smtp_server)
	message = 'email_track test by python!'
	temp_server.create_message(message)
	temp_server.connect()
	print('\r\n')

def recieve_block(chain):
	block = blockchain.Block()
	block_message = None
	user = input('Email user: ')
	password = input('User password: ')
	pop3_server = input('POP3 server: ')
	#pop3_server = poplib.POP3_SSL('pop.googlemail.com', '995')
	#pop3_server = poplib.POP3_SSL(pop3_server, '995')
	temp_server = email_track.fetch_email(user, password, pop3_server)
	temp_server.connect()
	temp_server.decode_email()
	block_message = temp_server.block_message
	block.add_message(blockchain.Email_Content(block_message))
	chain.add_block(block)
	print('add successfully, block: ', block)
	print('\r\n')

def print_info(chain, index = None): 
	if not chain:
		print('no index\n')
		return False

	temp_block = chain.chain[index]
	print('Block in index %d: ' % index, temp_block)
	for temp_message in temp_block.messages :
		"""
			temp_message is Email_Content object
			temp_block is Block object
			print the message id of the block
		"""
		print('No. %d %s' % (temp_block.messages.index(temp_message), '-'*60))
		print('ID : %s' % temp_message.id)

def print_chain(chain):
	for block in chain.chain:
		print(block)
		print('-------------------->')


def judge_spam(chain, index, spam_chain, model, dictionary):
	message_block = chain.chain[index]
	for message in message_block.messages:
		content = message.content
		result_matrix = spam_filter.judge(content, model, dictionary)	#retunr confusion matrix
		if result_matrix[0][0]:
			print('The mail is Ham')
		else:
			print('The mail is Spam, store the spam in spam_chain')
			block = blockchain.Block()
			block.add_message(message)
			spam_chain.add_block(block)

def manager():
	chain = blockchain.Chain()
	spam_chain = blockchain.Chain()
	block = blockchain.Block()
	flag = True

	#mining text data
	#filter by naive bayes

	'''
	input feature_result.csv
	'''
	df = pd.read_csv('feature_result.csv' ,header = None)
	train_matrix = df.values
	model, dictionary = spam_filter.train(train_matrix)

	while flag:
		print("\n####Email tracking demon by blockchain####")
		option ="""
		Action set:
			(1) send email by smtp
			(2) recieve&record in blockchain email by pop3
			(3) show the email content(block)
			(4) show the whole email chain
			(5) judge the spam & store in spam chain
			(6) show the spam chain
			(7) exit
				"""
		print(option)
		decide = input('-->Enter: ')
		if decide == '1':
			send_block()
		elif decide == '2':
			recieve_block(chain)
		elif decide == '3':
			index = int(input('input the index of the block: '))
			print_info(chain, index)
		elif decide == '4':
			if len(chain.chain) > 0:
				print_chain(chain)
			else:
				print('no block in the chain')
		elif decide == '5':
			if len(chain.chain) > 0:
				index = int(input('input the index of the block: '))
				judge_spam(chain, index, spam_chain, model, dictionary)
			else:
				print('No block')
		elif decide == '6':
			if len(spam_chain.chain) > 0:
				print_chain(spam_chain)
			else:
				print('No spam eamil in the chain')
		elif decide == '7':
			print('\nexit')
			flag = False

if __name__ == '__main__':
	manager()