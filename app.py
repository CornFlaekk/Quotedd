import flask
import flask_login
import sirope
import json
import datetime

from model.UserDto import User
from model.QuoteDto import Quote
from model.QuoteListsDto import QuoteList
from model.CommentDto import Comment

def create_app():
    lmanager = flask_login.login_manager.LoginManager()
    flapp = flask.Flask(__name__)
    sirp = sirope.Sirope()
    
    flapp.config.from_file("cfg/config.json", load=json.load)
    lmanager.init_app(flapp)
    return flapp, lmanager, sirp

app, lm, srp = create_app()


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
    quotelists = list(srp.load_all(QuoteList))
    
    for quote in last_quotes:
        quote.safe_id = quote.get_safe_id(srp) 
        quote.quotelists_names = []
        for quotelist in quotelists:
            if quote.safe_id in quotelist.quote_ids:
                name = f"✓ {quotelist.name}"
                quote.quotelists_names.append(name)
            else:
                quote.quotelists_names.append(quotelist.name)
        
    for quotelist in quotelists:
        quotelist.quotes = []
        for quote_id in quotelist.quote_ids:
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
    q.srp_save(srp)
    
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
    quote_safe_id = flask.request.form.get("quoteSafeID")
    if quotelist_name[:2] == "✓ ":
        quotelist = srp.find_first(QuoteList, lambda ql: ql.name == quotelist_name[2:])     
        quotelist.remove_quote_id(quote_safe_id)
        quotelist.srp_save(srp)
    else:
        quotelist = srp.find_first(QuoteList, lambda ql: ql.name == quotelist_name)
        quotelist.add_quote_id(quote_safe_id)
        quotelist.srp_save(srp)
        
    origin_page = flask.request.environ.get("HTTP_REFERER")
    return flask.redirect(origin_page, 302)

@app.route("/quotes/quote", methods=["GET"])
def quote_page():
    quote_safe_id = flask.request.args.get("quoteSafeID")
    quote_oid = srp.oid_from_safe(quote_safe_id)
    quote = srp.load(quote_oid)
    quote.safe_id = quote_safe_id
    
    quotelists = list(srp.load_all(QuoteList))
    quote.quotelists_names = []
    for quotelist in quotelists:
            if quote.safe_id in quotelist.quote_ids:
                name = f"✓ {quotelist.name}"
                quote.quotelists_names.append(name)
            else:
                quote.quotelists_names.append(quotelist.name)
                
    comments = list(srp.filter(Comment, lambda c: c.quote_id == quote.safe_id))
    quote.comments = comments
                    
    values = {
        "quote" : quote
    }
    return flask.render_template("quote_page.html", **values)

@app.route("/quotes/quote/comments/add", methods=["POST"])
def add_comment():
    quote_safe_id = flask.request.form.get("quoteSafeID")
    comment_content = flask.request.form.get("commentContent")
    comment_date = datetime.datetime.now()
    c = Comment(comment_content, quote_safe_id, comment_date)
    c.srp_save(srp)
    
    origin_page = flask.request.environ.get("HTTP_REFERER")
    return flask.redirect(origin_page, 302)
    

if __name__ == "__main__":
       flask.run()