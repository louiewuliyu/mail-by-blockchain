l = ['l', 'o', 'u', 'i', 'e']
print(type(l))
size = 0
for x in l:
	size += len(x.encode('utf-8'))
print(size, '\n')


import hashlib

a = 'testing string(測試)'
a = bytearray(str(a), 'utf-8')
print('a: ', a)
print(hashlib.sha256(a).hexdigest())

