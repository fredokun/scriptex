import re

VAR_TOKEN_START = '{{'
VAR_TOKEN_END = '}}'

INST_TOKEN_START = '{%'
INST_TOKEN_END = '%}'

TOKEN_REGEX = re.compile(r"(%s.*?%s|%s.*?%s)" 
                         % (VAR_TOKEN_START,
                            VAR_TOKEN_END,
                            INST_TOKEN_START,
                            INST_TOKEN_END))

with open('basic.tango.tex') as content_file:
    content = content_file.read()


tab = TOKEN_REGEX.split(content)

dict = { 'var1' : 1 , 'var2' :2 }

for i in range(len(tab)) :
    if re.match("^\{\{.*\}\}$",tab[i]) is not None :
        tab[i]=re.sub("^\{\{(.*)\}\}$",dict[\1],tab[i])

print(tab)

