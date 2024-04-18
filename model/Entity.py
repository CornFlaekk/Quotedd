class Entity:
    def __init__(self) -> None:
        self.__oid = -1
        
    @property
    def oid(self):
        return self.__oid
        
    def srp_save(self, srp):
        self.__oid = srp.save(self)
        srp.save(self)
        return self.oid
    
    def get_safe_id(self, srp):
        return srp.safe_from_oid(self.oid)