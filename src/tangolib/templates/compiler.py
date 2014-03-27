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
        print(self.document.compile(self.data))
        return "".join(self.document.compile(self.data))
