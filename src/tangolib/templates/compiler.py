from markup import Text,Each,Call,Variable,Document


class CompilerError(Exception):
    pass


class Compiler:


    def __init__(self,document,data):
        self.document=document
        self.data=data
        self.initializeGlobalEnvironment()
    
    def __initializeGlobalEnvironment(self):
        self.globalEnvironment = {}
        
        
    def process(self):
        
        for i in range(len(self.document)) :
            if isinstance(self.document[i],Variable):
                # TODO
            elif isinstance(self.document[i],Each):
                # TODO
            elif isinstance(self.document[i],Call):
                # TODO
