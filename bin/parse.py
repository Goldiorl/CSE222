import re

f  = open('meter500.txt','r')

data = f.readlines()

for line in data:
    returnValue = re.findall(r'\s\d\d\d\s', line)
    for value in returnValue:
        print value


