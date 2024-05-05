from model.Entity import Entity

class Quote(Entity):
    def __init__(self, content, book, author, date, user):
        Entity.__init__(self, user)
        self.__content = content
        self.__book = book
        self.__author = author
        self.__date = date
    
    @property
    def content(self):
        return self.__content
    
    def set_content(self, content):
        self.__content = content
    
    @property
    def book(self):
        return self.__book
    
    def set_book(self, book):
        self.__book = book
    
    @property
    def author(self):
        return self.__author
    
    def set_author(self, author):
        self.__author = author
    
    @property
    def date(self):
        return self.__date
    
    
    def __str__(self) -> str:
        return f"\"{self.content}\", from {self.book} by {self.author}. Posted by {self.user}"