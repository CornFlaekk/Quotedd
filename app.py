import flask
import flask_login
import sirope
import json
from model.User import User
from model.CitaDto import Cita

def create_app():
    lmanager = flask_login.login_manager.LoginManager()
    flapp = flask.Flask(__name__)
    sirp = sirope.Sirope()
    
    flapp.config.from_file("cfg/config.json", load=json.load)
    lmanager.init_app(flapp)
    return flapp, lmanager, sirp


app, lm, srp = create_app()

cita2 = Cita("Mi pinga 2", "La pinga 2", "The pinga")
cita2_oid = srp.save(cita2)
for cita in srp.load_all(Cita):
    print(cita)
print(srp.load(cita2_oid))

@lm.user_loader
def user_loader(id: str) -> User:
    return User.find(srp, id)
...

@lm.unauthorized_handler
def unauthorized_handler():
    flask.flash("Unauthorized user")
    return flask.redirect("/")
...

@app.route("/", methods=["GET"])
def main():
    return flask.send_file("index.html")

@app.route("/home", methods=["GET"])
def home():
    pass

if __name__ == "__main__":
       flask.run()