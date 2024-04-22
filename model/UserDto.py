import flask_login
import werkzeug.security as safe
import sirope

class User(flask_login.mixins.UserMixin):
    def __init__(self, name, email, passwd):
        self.__name = name
        self.__email = email
        self.__passwd = safe.generate_password_hash(passwd)
        
    @property
    def name(self):
        return self.__name    
        
    @property
    def email(self):
        return self.__email
    
    def get_id(self):
        return self.name
    
    def compare_passwd(self, another_passwd):
        return safe.check_password_hash(self.__passwd, another_passwd)
    
    @staticmethod
    def current():
        usr = flask_login.current_user
        
        if usr.is_anonymous:
            flask_login.logout_user() 
            usr = None

        return usr
    
    @staticmethod
    def find(srp: sirope.Sirope, username: str) -> "User":
        user = srp.find_first(User, lambda u: u.name == username)
        return user
