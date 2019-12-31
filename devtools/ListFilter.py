import re


class ListFilter:
    def __init__(self, array):
        self.array = array
        self.result = []
        self.keyin = lambda x: x

    def key(self, element):
        return True

    def found(self, element):
        print(element)

    def filter(self):
        self.result.clear()
        for element in self.array:
            if (self.key(self.keyin(element))):
                self.found(element)
                self.result.append(element)
        return self.result


class RegexListFilter(ListFilter):
    def __init__(self, array):
        self.array = array
        self.result = []
        self.pattern = None

    def key(self, element):
        return self.pattern.match(element) is not None
