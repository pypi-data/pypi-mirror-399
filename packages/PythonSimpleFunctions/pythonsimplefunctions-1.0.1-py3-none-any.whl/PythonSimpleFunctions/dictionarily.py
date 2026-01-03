class Dictionarily:
    def __init__(self):
        self.content = {}
    
    def add(self, key, value):
        self.content[key] = value
    
    def sort(self):
        a = 0
        temp = list(self.content.items())
        while a < len(temp) - 1:
            if str(temp[a]) > str(temp[a + 1]):
                temp[a], temp[a + 1] = temp[a + 1], temp[a]
                a = 0
            else:
                a += 1
        self.content = dict(temp)
    
    def sortNumbersFirst(self):
        a = 0
        temp = list(self.content.items())
        while a < len(temp) - 1:
            if str(temp[a]) > str(temp[a + 1]):
                temp[a], temp[a + 1] = temp[a + 1], temp[a]
                a = 0
            else:
                a += 1
        self.content = dict(sorted(dict(temp).items(), key=lambda item: (isinstance(item[0], str), item[0])))
    
    def show(self):
        return self.content