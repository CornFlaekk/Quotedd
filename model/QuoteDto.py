from model.Entity import Entity

class Quote(Entity):
    def __init__(self, content, book, author, date):
        Entity.__init__(self)
        self.__content = content
        self.__book = book
        self.__author = author
        self.__date = date
        #self.__user_dto = user_dto
    
    @property
    def content(self):
        return self.__content
    
    @property
    def book(self):
        return self.__book
    
    @property
    def author(self):
        return self.__author
    
    @property
    def date(self):
        return self.__date
    
    #@property
    #def user_dto(self):
    #    return self.__user_dto
    
    def __str__(self) -> str:
        return f"\"{self.content}\", from {self.book} by {self.author}. Posted on {self.date}"