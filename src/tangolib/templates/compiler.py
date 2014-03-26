class CompilerError(Exception):
    pass


class Compiler:


    def __init__(self,document,data):
        self.document=document
        self.data=data
        #self.initializeGlobalEnvironment()
    

    def __initializeGlobalEnvironment(self):
        self.globalEnvironment = {}
        # TODO for callable
        
    def process(self):
        return self.document.compile(self.data)
