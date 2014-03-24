class Node:

    def __init__(self):
        self.children=[]

    def addChild(self,node):
        self.children.append(node)


class Text:
    
    def __init__(self,content):
        self.content=content

class Each:
    
    def __init__(self,arg):
        self.arg=arg


class Call:
    
    def __init__(self,arg):
        self.arg=arg

class Variable:
    
    def __init__(self,name):
        self.name=name

class End : 
    pass
