from model.Entity import Entity

class Comment(Entity):
    def __init__(self, content, quote_id, date):
        Entity.__init__(self)
        self.__content = content
        self.__quote_id = quote_id      #Quote safe ID
        self.__date = date
        
    @property
    def content(self):
        return self.__content
    
    @property
    def quote_id(self):
        return self.__quote_id
    
    @property
    def date(self):
        return self.__date
    
    def __str__(self) -> str:
        return f"{self.content} [Posted on {self.date}]"