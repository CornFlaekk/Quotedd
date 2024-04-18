import flask
import flask_login
import sirope
import json
import datetime

from model.UserDto import User
from model.QuoteDto import Quote
from model.QuoteListsDto import QuoteList

def create_app():
    lmanager = flask_login.login_manager.LoginManager()
    flapp = flask.Flask(__name__)
    sirp = sirope.Sirope()
    
    flapp.config.from_file("cfg/config.json", load=json.load)
    lmanager.init_app(flapp)
    return flapp, lmanager, sirp


app, lm, srp = create_app()
ql = srp.load_first(QuoteList, 1)
#print(ql)
#cita2 = Cita("Mi pinga 2", "La pinga 2", "The pinga")
#cita2_oid = srp.save(cita2)
#for cita in srp.load_all(Cita):
#    print(cita)
#print(srp.load(cita2_oid))

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
    last_quotes = list(srp.load_last(Quote, 10))
    for quote in last_quotes:
        quote.safe_id = quote.get_safe_id(srp) 
    
    quotelists = list(srp.load_all(QuoteList))
    for quotelist in quotelists:
        print(f"{quotelist=}")
        quotelist.quotes = []
        for quote_id in quotelist.quote_ids:
            print(f"{quote_id=}")
            quote_oid = srp.oid_from_safe(quote_id)
            quote = srp.load(quote_oid)
            quote.safe_id = quote_id
            quotelist.quotes.append(quote)

    values = {
        "last_quotes" : last_quotes,
        "quotelists"  :quotelists
    }
    
    return flask.render_template("home.html", **values)

@app.route("/quote/add", methods=["POST"])
def add_quote():
    quote_content = flask.request.form.get("quoteContent")
    quote_book = flask.request.form.get("quoteBook")
    quote_author = flask.request.form.get("quoteAuthor")
    quote_date = datetime.datetime.now()
    q = Quote(quote_content, quote_book, quote_author, quote_date)
    print(f"OID: {q.srp_save(srp)}")
    print(f"OID_2: {q.oid}")
    
    return flask.redirect("/home", 302)

@app.route("/quotelists/add", methods=["POST"])
def add_quotelist():
    quotelist_name = flask.request.form.get("quotelistName")
    quotelist_desc = flask.request.form.get("quotelistDesc")
    ql = QuoteList(quotelist_name, quotelist_desc)
    ql.srp_save(srp)
    return flask.redirect("/home", 302)

@app.route("/quotelists/quotelist/add_song", methods=["POST"])
def add_song_quotelist():
    quotelist_name = flask.request.form.get("quotelistName")
    print(f"{quotelist_name=}")
    quote_safe_id = flask.request.form.get("quoteSafeID")
    quotelist = srp.find_first(QuoteList, lambda ql: ql.name == quotelist_name)
    quotelist.add_quote_id(quote_safe_id)
    quotelist.srp_save(srp)
    
    return flask.redirect("/home", 302)

if __name__ == "__main__":
       flask.run()