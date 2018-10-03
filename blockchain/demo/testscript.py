import spam_filter
import blockchain
from sklearn.naive_bayes import MultinomialNB

import pandas as pd
import numpy as np
import matplotlib as mlt
import time
import os
import hashlib


def add_block(chain):
    train_dir = 'ling-spam\\train-mails'
    emails = [os.path.join(train_dir, f) for f in os.listdir(train_dir)]
    print(emails[0])
    block_msg = None

    for mail in emails[601:]:
    	context = None
    	with open(mail) as file:
    		context = file.read()
    		#print(context)
    	block_msg = context
    	block = blockchain.Block()
    	block.add_message(blockchain.Email_Content(block_msg))
    	#print(len(chain.chain))
    	chain.add_block(block)

    print(len(emails[601:]))
    # print(chain.chain[0])
    # print(chain.chain[1])
    return emails[601:]

chain = blockchain.Chain()	#chain for spam
spam_chain = blockchain.Chain()
block = blockchain.Block()
test_num = 0
'''
mining text data
filter by naive bayes
input feature_result.csv
'''
df = pd.read_csv('feature_result.csv', header=None)
train_matrix = df.values
model, dictionary = spam_filter.train(train_matrix)
spam_list = add_block(chain)	#return the list of spam

# temp = chain.chain[0].messages[0].content_hash
# print(temp)
# print(hashlib.sha256(bytearray(spam_list[0], 'utf-8')).hexdigest())
spam_list.sort()
mail_hash = []

#10 sample spam
for mail in spam_list:
    with open(mail) as file:
	    context = file.read()
	    mail_hash.append(hashlib.sha256(bytearray(context, 'utf-8')).hexdigest())

#start
times_chain = []
for mail in mail_hash:	
	subtime = 0
	for i in range(1,10):
		start = time.clock()
		for block in chain.chain:
			if block.messages[0].content_hash == mail:
				break;
		end = time.clock()
		subtime += (end-start)

	sub_mean = subtime/10.0
	times_chain.append(sub_mean)

mean = sum(times_chain)/len(mail_hash)
print(mean)

#########################

# df = pd.read_csv('feature_result.csv' ,header = None)
# train_matrix = df.values
# model, dictionary = spam_filter.train(train_matrix)
# times_learning = []
# for i in spam_list:
#     words = []
#     context = None
#     with open(i) as file:
# 	    context = file.read()
# 	    #print(context)
#     subtime = 0
#     for i in range(1, 10):
#     	start = time.clock()
#     	result = spam_filter.judge(context, model, dictionary)
#     	end = time.clock()
#     	subtime += (end-start)
#     	sub_mean = subtime/10.0
#     	times_learning.append(sub_mean)
# mean_learning = sum(times_learning)/len(spam_list)
# print(mean_learning)
# print(len(spam_list))
