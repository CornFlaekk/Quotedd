from model.Entity import Entity

class QuoteList(Entity):
    def __init__(self, name, description, user):
        Entity.__init__(self, user)
        self.__name = name
        self.__description = description
        self.__quote_ids = []  #Quote IDs are their safe IDs

    @property
    def name(self):
        return self.__name
    
    def set_name(self, name):
        self.__name = name
    
    @property
    def description(self):
        return self.__description
    
    def set_description(self, description):
        self.__description = description
    
    @property
    def quote_ids(self):
        return self.__quote_ids
    
    # --- QUOTE MANAGEMENT --- 
    
    def add_quote_id(self, quote_id):
        if quote_id not in self.quote_ids:
            self.quote_ids.append(quote_id)
        
    def remove_quote_id(self, quote_id):
        if quote_id in self.quote_ids:
            self.quote_ids.remove(quote_id)