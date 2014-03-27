import re

from markup import Text,Each,Call,Variable,End

# Start TOKEN
VAR_TOKEN_START = '{{'
VAR_TOKEN_END = '}}'

INST_TOKEN_START = '{%'
INST_TOKEN_END = '%}'

TOKEN_REGEX = re.compile(r"(%s.*?%s|%s.*?%s)" 
                         % (VAR_TOKEN_START,
                            VAR_TOKEN_END,
                            INST_TOKEN_START,
                            INST_TOKEN_END))
# End TOKEN


class Lexer:

    def __init__(self,content):
        self.content=content

    def process(self):
        
        matchedElem = None
        splitTokenFromContent = TOKEN_REGEX.split(self.content)
        tokenizedContent = []

        varToken = re.compile("^%s(\s*)(.+?)(\s*)%s$" % (VAR_TOKEN_START,VAR_TOKEN_END))
        eachInstToken = re.compile("^%s(\s*)each(\s*)(.+?)(\s*)%s$" % (INST_TOKEN_START,INST_TOKEN_END))
        callInstToken = re.compile("^%s(\s*)call(\s*)(.+?)(\s*)%s$" % (INST_TOKEN_START,INST_TOKEN_END))
        endInstToken = re.compile("^%s(\s*)end(\s*)%s$"  % (INST_TOKEN_START,INST_TOKEN_END))
        

        for elem in splitTokenFromContent :
            matchedElem = varToken.match(elem)
            if matchedElem :
                tokenizedContent.append(Variable(matchedElem.group(2)))
            else : 
                matchedElem = eachInstToken.match(elem)
                if matchedElem :
                    tokenizedContent.append(Each(matchedElem.group(3)))
                else:
                    matchedElem = callInstToken.match(elem)
                    if matchedElem :
                        tokenizedContent.append(Call(matchedElem.group(3)))
                    else:
                        matchedElem = endInstToken.match(elem)
                        if matchedElem :
                            tokenizedContent.append(End())
                        else:
                            tokenizedContent.append(Text(elem))

        return tokenizedContent
            
