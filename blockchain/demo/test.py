import numpy
from sklearn.metrics import confusion_matrix

test_labels = numpy.zeros((2, 3))
#test_labels[130:260] = 1
print(test_labels)
print(len(test_labels))

y_true = [2, 1, 0, 1, 2, 0]
y_pred = [2, 0, 0, 1, 2, 1]
c = confusion_matrix(y_true, y_pred)
print(c)

s = 'hello python'
s = s.split()
for x in s:
	print(x)

l = [[0]]
print(l[0][0])

mail_dir = ['hello python', 'hi']
words = []
for string in mail_dir:
	words += string.split()

print(words)

