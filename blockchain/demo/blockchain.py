import json
import hashlib
import time
import datetime
import email_track

import poplib

class Email_Content(object):
	"""docstring for email_content"""
	def __init__(self, content):
		super(Email_Content, self).__init__()
		self.content = content	#list #string
		self.id = content[:-1]
		#self.timestamp = time.time()
		self.timestamp = time.asctime(time.localtime(time.time()))
		self.hash = None
		self.pre_hash = None
		self.content_hash = self._hash_content(self.content)
		self.payload_hash = self._hash_payload()
		self.size = self.get_size 	#length in bytes

	def _hash_content(self, content):
		return hashlib.sha256(bytearray(content, 'utf-8')).hexdigest()
		
	def get_size(self, content):
		size = 0
		for x in content:
			size += len(x.encode('utf-8'))
		return size
		
	def _hash_payload(self):
		return hashlib.sha256(bytearray(str(self.timestamp) + str(self.content) + str(self.id), "utf-8")).hexdigest()

	def _hash_message(self):
		return hashlib.sha256(bytearray(str(self.pre_hash) + self.payload_hash, "utf-8")).hexdigest()

	def link(self, message):
		self.pre_hash = message.hash

	def seal(self):
		self.hash = self._hash_message()	#Get the message hash.

	def validate(self):
		""" Check whether the message is valid or not. """
		if self.payload_hash != self._hash_payload():
			raise InvalidMessage("Invalid payload hash in message: " + str(self))
		if self.hash != self._hash_message():
			raise InvalidMessage("Invalid message hash in message: " + str(self))

	def __repr__(self):
		return 'Message<hash: {}, pre_hash: {}, data: {}>'.format(
			self.hash, self.pre_hash, self.content[:20]
		)

#block object
class Block(object):
	"""docstring for block"""
	def __init__(self):
		super(Block, self).__init__()
		self.messages = []
		self.timestamp = None
		self.hash = None
		self.pre_hash = None
		
	def _hash_block(self):
		return hashlib.sha256(bytearray(str(self.pre_hash) + str(self.timestamp) + self.messages[-1].hash, "utf-8")).hexdigest()

	def add_message(self, message):
		if len(self.messages) > 0:
			message.link(self.messages[-1])
		message.seal()
		message.validate()
		self.messages.append(message)

	def  link(self, block):
		self.pre_hash = block.hash

	def seal(self):
		#self.timestamp = time.time()
		self.timestamp  = time.asctime(time.localtime(time.time()))
		self.hash = self._hash_block()

	def validate(self):
		""" Validates each message hash, then chain integrity, then the block hash.
			Calls each message's validate() method.

			If a message fails validation, this method captures the exception and 
			throws InvalidBlock since an invalid message invalidates the whole block.
		"""
		for i, msg in enumerate(self.messages):
			try:
				msg.validate()
				if i > 0 and msg.pre_hash != self.messages[i-1].hash:
					raise InvalidBlock("Invalid block: Message #{} has invalid message link in block: {}".format(i, str(self)))
			except InvalidMessage as ex:
				raise InvalidBlock("Invalid block: Message #{} failed validation: {}. In block: {}".format(
					i, str(ex), str(self))
				)

	def __repr__(self):
		return 'Block<hash: {}, pre_hash: {}, messages: {}, time: {}>'.format(
			self.hash, self.pre_hash, len(self.messages), self.timestamp
		)

class Chain(object):
	"""docstring for Chain"""
	def __init__(self):
		super(Chain, self).__init__()
		self.chain = []

	def add_block(self, block):
		#add valid block
		if len(self.chain) > 0:
			#print('test')
			block.pre_hash = self.chain[-1].hash
		block.seal()
		block.validate()
		self.chain.append(block)

	def validate(self):
		""" Validates each block, in order.
			An invalid block invalidates the chain.
		"""
		for i, block in enumerate(self.simple_chain):
			try:
				block.validate()
			except InvalidBlock as exc:
				raise InvalidBlockchain("Invalid blockchain at block number {} caused by: {}".format(i, str(exc)))
		return True

	def __repr__(self):
		return 'SimpleChain<blocks: {}>'.format(len(self.chain))

class InvalidMessage(Exception):
	def __init__(self,*args,**kwargs):
		Exception.__init__(self,*args,**kwargs) 

class InvalidBlock(Exception):
	def __init__(self,*args,**kwargs):
		Exception.__init__(self,*args,**kwargs)

class InvalidBlockchain(Exception):
	def __init__(self,*args,**kwargs):
		Exception.__init__(self,*args,**kwargs) 
