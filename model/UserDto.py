import flask_login
import werkzeug as safe
import sirope

class User(flask_login.mixins.UserMixin):
    def __init__(self, email, passwd):
        self.__email = email
        self.__passwd = safe.generate_password_hash(passwd)
        
    @property
    def email(self):
        return self.__email
    
    def compare_passwd(self, another_passwd):
        return safe.check_password_hash(another_passwd)
    
    @staticmethod
    def current_user():
        usr = flask_login.current_user
        
        if usr.is_anonymous:
            usr.logout_user() 
            usr = None

        return usr
    
    @staticmethod
    def find(srp: sirope.Sirope, email: str) -> "User":
        return srp.find_first(User, email)
    ...
...