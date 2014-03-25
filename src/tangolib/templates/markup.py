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
        
    

class Text(Node):
    
    def __init__(self,content):
        super().__init__()
        self.content=content


    def toString(self):
        return "Text"

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


class End(Node): 
    pass
