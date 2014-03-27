from compiler import CompilerError

import re

class Node:
    def __init__(self):
        self.children=[]

    def addChild(self,node):
        self.children.append(node)


class Document(Node):

    def __init__(self,children):
        super().__init__()
        self.children=children

    def addChild(self,node):
        self.children.append(node)
        
    
    def compile(self,globalEnvironment):
        compiledChildren =[]

        for elem in self.children:
            compiledChildren.append(elem.compile(globalEnvironment))

        return compiledChildren

class Text(Node):
    
    def __init__(self,content):
        super().__init__()
        self.content=content

    def toString(self):
        return "Text"

    def compile(self,globalEnvironment):
        return self.content


class Each(Node):
    
    def __init__(self,arg):
        super().__init__()
        self.arg=arg

    def append(self,node):
        super().addChild(node)

    def toString(self):
        print("Each")

        for elem in self.children:
            print("\t"+elem.toString())

    def compile(self,globalEnvironment):
        compiledContent=[]
        iterable = None

        if re.match('^\[([a-zA-Z0-9]+,)*[a-zA-Z0-9]+\]$',self.arg) :
            iterable=eval(self.arg)
        else :
            iterable = valueOfEnvironment(self.arg,globalEnvironment)
            if re.match('^\[([a-zA-Z0-9]+,)*[a-zA-Z0-9]+\]$',iterable) :
                iterable=eval(iterable)    
            else :
                raise CompilerError("The value is not iterable")


        for elem in iterable:
            for child in self.children:
                compiledContent.append(child.compile(globalEnvironment))


        return "".join(compiledContent)

                

class Call(Node):
    
    def __init__(self,arg):
        super().__init__()
        self.arg=arg

    def toString(self):
        print("Call")


class Variable(Node):
    
    def __init__(self,name):
        super().__init__()
        self.name=name
        
    
    def toString(self):
        print("Variable")

    
    def compile(self,globalEnvironment):
        return valueOfEnvironment(self.name,globalEnvironment)

class End(Node): 
    pass





# Usefull functions

def valueOfEnvironment(path,globalEnvironment):
    path = path.split('.')
    hashMap = globalEnvironment

    for i in range(len(path)):
        if path[i] in hashMap:
            hashMap=hashMap[path[i]]
        else:
            raise CompilerError("Global environment doesn't contain the value of the variable")
        
    return hashMap
    
