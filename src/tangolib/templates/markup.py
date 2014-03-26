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
        import pdb; pdb.set_trace()
        print("Each")

        for elem in self.children:
            print("\t"+elem.toString())

    def compile(self,globalEnvironment):
        compiledContent=[]
        listIterable = None

        print(globalEnvironment)
        print(self.arg)
        print(re.match('\[([a-zA-Z0-9]+,)*[a-zA-Z0-9]+\]',self.arg))

        #TODO
        # Eval l'argument par eval()
        if re.match("^\[(\w+,)*(\w)+\]$",self.arg):
            listIterable=eval(self.arg)
        # OU check si la valeur est dans globalenv
        else: 
            path = self.arg.split('.')
            hashMap = globalEnvironment
        
            for i in range(len(path)):
                if path[i] in hashMap:
                    hashMap=hashMap[path[i]]
                else:
                    raise CompilerError("Global environment doesn't contain the value of the variable")

            if re.match("^\[([a-zA-Z0-9]+\,)*[a-zA-Z0-9]+\]$",hashMap):
                listIterable=eval(hashMap)
            else:
                #TODO
                raise CompilerError("TODO")
            

        for elem in listIterable:
            for child in self.children:
                compiledContent.append(child.compile(globalEnvironment))


        return compiledContent

                

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
        path = self.name.split('.')
        hashMap = globalEnvironment

        for i in range(len(path)):
            if path[i] in hashMap:
                hashMap=hashMap[path[i]]
            else:
                raise CompilerError("Global environment doesn't contain the value of the variable")

        return hashMap

class End(Node): 
    pass
