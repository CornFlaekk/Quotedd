class Entity:
    def __init__(self, user) -> None:
        self.__oid = -1
        self.__user = user
    
    @property
    def user(self):
        return self.__user    
    
    @property
    def oid(self):
        return self.__oid
        
    def srp_save(self, srp):
        self.__oid = srp.save(self)
        srp.save(self)
        return self.oid
    
    def get_safe_id(self, srp):
        return srp.safe_from_oid(self.oid)