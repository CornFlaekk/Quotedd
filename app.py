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
    
    flapp.config.from_file("instance/config.json", load=json.load)
    lmanager.init_app(flapp)
    return flapp, lmanager, sirp

app, lm, srp = create_app()


@lm.user_loader
def user_loader(username: str) -> User:
    return User.find(srp, username)


@lm.unauthorized_handler
def unauthorized_handler():
    flask.flash("Unauthorized user")
    return flask.redirect("/login")


@app.route("/", methods=["GET"])
def main():
    user = User.current()
    print(user)
    if user is None:
        return flask.send_file("static/index.html")
    else:
        return flask.redirect("/home")


# > LOGIN <
@app.route("/login", methods=["GET", "POST"])
def login():
    if flask.request.method == "GET":
        return flask.send_file("static/login.html")
    else:
        user_name = flask.request.form.get("userName")
        user_password = flask.request.form.get("userPassword")
        user = User.find(srp, user_name)
        
        if user is None or not user.compare_passwd(user_password):
            flask.flash("Incorrect login credentials")
            return flask.redirect("/login")
        else:
            flask.flash("Login successful")
            flask_login.login_user(user, force=True)
            return flask.redirect("/home")


# > LOGOUT <
@flask_login.login_required
@app.route("/logout", methods=["GET"])
def logout():
    flask_login.logout_user()
    return flask.redirect("/")


# > REGISTER <
@app.route("/register", methods=["GET", "POST"])
def register():
    if flask.request.method == "GET":
        return flask.send_file("static/register.html")
    else:
        user_name = flask.request.form.get("userName")
        user_email = flask.request.form.get("userEmail")
        user_password = flask.request.form.get("userPassword")
        
        u = User(user_name, user_email, user_password)
        srp.save(u)
        flask.flash("User registered")
        return flask.redirect("/login")


# > HOME PAGE <
@flask_login.login_required
@app.route("/home", methods=["GET"])
def home():
    user = flask_login.current_user
    try:
        user.name
    except AttributeError:
        return flask.redirect("/login")
    
    last_quotes = list(srp.load_last(Quote, 10))
    quotelists = list(srp.filter(QuoteList, lambda ql: ql.user == user.name))
    
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
        "quotelists"  :quotelists,
        "user" : user
    }
    
    return flask.render_template("home.html", **values)


# > ADD QUOTE <
@app.route("/quote/add", methods=["POST"])
def add_quote():
    quote_content = flask.request.form.get("quoteContent")
    quote_book = flask.request.form.get("quoteBook")
    quote_author = flask.request.form.get("quoteAuthor")
    quote_date = datetime.datetime.now()
    user = User.current()
    q = Quote(quote_content, quote_book, quote_author, quote_date, user.name)
    q.srp_save(srp)
    
    return flask.redirect("/home", 302)


# > ADD QUOTELIST <
@app.route("/quotelists/add", methods=["POST"])
def add_quotelist():
    quotelist_name = flask.request.form.get("quotelistName")
    quotelist_desc = flask.request.form.get("quotelistDesc")
    user = User.current()
    ql = QuoteList(quotelist_name, quotelist_desc, user.name)
    ql.srp_save(srp)
    return flask.redirect("/home", 302)


# > ADD QUOTE TO QUOTELIST <
@app.route("/quotelists/quotelist/add_quote", methods=["GET"])
def add_quote_quotelist():
    
    quotelist_name = flask.request.args.get("quotelistName")
    quote_safe_id = flask.request.args.get("quoteSafeID")
    
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


# > VIEW QUOTE PAGE <
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


# > ADD COMMENT TO QUOTE <
@app.route("/quotes/quote/comments/add", methods=["POST"])
def add_comment():
    quote_safe_id = flask.request.form.get("quoteSafeID")
    comment_content = flask.request.form.get("commentContent")
    comment_date = datetime.datetime.now()
    user = User.current()
    c = Comment(comment_content, quote_safe_id, comment_date, user.name)
    c.srp_save(srp)
    
    origin_page = flask.request.environ.get("HTTP_REFERER")
    return flask.redirect(origin_page, 302)
    

if __name__ == "__main__":
       flask.run()