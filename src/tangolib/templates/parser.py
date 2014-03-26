from markup import Each,End,Document

class Parser:

    def __init__(self,tokenizedContent):
        self.tokenizedContent=tokenizedContent

    def process(self):
        
        parsedContent=[]

        self.__nestedStructureFactory(self.tokenizedContent,
                                      parsedContent)

        doc = Document(parsedContent)
        
        return doc


    def __nestedStructureFactory(self,tokenList,storeList):
        
        
        if not tokenList:
            return []

        car = tokenList.pop(0)

        if isinstance(car,Each):
            instEach = self.__nestedStructureFactory(tokenList,car)
            storeList.append(instEach)
            return self.__nestedStructureFactory(tokenList,storeList)
        elif isinstance(car,End):
            return storeList
        else:
            storeList.append(car)
            return self.__nestedStructureFactory(tokenList,storeList)
