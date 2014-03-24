from markup import Text,Each,Call,Variable,End

class Parser:

    def __init__(self,tokenizedContent):
        self.tokenizedContent=tokenizedContent

    def process(self):
        
        openCurly=0
        closeCurly=0
        elem=None    
        astOutput=[]

        for i in range(len(self.tokenizedContent)) :
            elem = self.tokenizedContent[i]
            if isinstance(elem,Each):
                openCurly=openCurly+1
            else:
                astOutput.append(elem)
                
