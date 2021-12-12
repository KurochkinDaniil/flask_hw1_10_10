import os
import sqlite3


from flask import Flask, render_template, url_for, request, flash, g, redirect, make_response
from  flask_database import FlaskDataBase
from bcrypt import gensalt, hashpw

DATABASE = "flask_app.db"
DEBUG = True
SECRET_KEY = 'ewazxYCVBN%%%894cghjk'
SALT = gensalt()

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['DEBUG'] = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flask_app.db')))

fdb = None

@app.before_request
def services():
    global fdb
    fdb = FlaskDataBase(get_db())

def if_logged_in(func):
    def wrapper(*args, **kwargs):
        if not request.cookies.get("logged"):
            return redirect(url_for("login"))
        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper

def if_not_logged_in(func):
    def wrapper(*args, **kwargs):
        if request.cookies.get("logged"):
            return redirect(url_for("index"))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

def create_db():
    db = connect_db()
    with app.open_resource("db_schem.sql", "r") as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()

def get_db():
    if not hasattr(g, "link_db"):
        g.link_db = connect_db()
    return g.link_db

def connect_db():
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    return conn

def register_user(email: str, password: str):
    password_hash = str(hashpw(password.encode(), SALT))
    fdb.add_new_user(email, password_hash)


def check_login_form(email: str, password: str) -> str:
    if not (email and password):
        return "All fields must be filled"

    user = FlaskDataBase(get_db()).get_user(email)
    if not user or not hashpw(password.encode(), SALT) != user[password].encode():
        return "email or password is incorrect"

    return ""


@app.route('/add_post', methods=['POST', 'GET'])
@if_logged_in
def add_post():
    logged = True if request.cookies.get("logged in") else False
    if request.method == "POST":
        title = request.form["name"]
        description = request.form["post"]
        res = fdb.add_post(title, description)
        if not res:
            flash("POST WAS INCORRECT", category="error")
        else:
            flash("SUCCESSFULLY", category="success")
    return render_template("add_post.html", menu_url=fdb.get_menu(), logged=logged)


@app.route("/all_posts")
@if_logged_in
def all_posts():
    logged = True if request.cookies.get("logged") else False
    posts = fdb.get_posts()
    print(dir(posts[0]))
    print(posts[0].keys())
    return render_template("all_posts.html", menu_url=fdb.get_menu(), posts=fdb.get_posts(), logged=logged)


@app.route("/post/<int:post_id>")
@if_logged_in
def post_content(post_id):
    logged = True if request.cookies.get("logged") else False
    title, description = fdb.get_post_content(post_id)

    return render_template("post_info.html", menu_url=fdb.get_menu(),
                           title=title, description=description, logged=logged)


@app.route('/')
def index():
    logged = True if request.cookies.get("logged") else False
    return render_template('index.html', menu_url=fdb.get_menu(),  logged=logged)


@app.route('/second')
def second():
    logged = True if request.cookies.get("logged") else False
    return render_template('second.html', menu_url=fdb.get_menu(),  logged=logged)


@app.route('/user/<username>')
def profile(username):
    return f"<h1>Hello {username}!</h1>"


@app.route('/login', methods=['POST', 'GET'])
@if_not_logged_in
def log_in():
    logged = True if request.cookies.get("logged") else False
    if request.method == 'GET':
        return render_template('login.html', menu_url=fdb.get_menu(),  logged=logged)

    email = request.form.get('email')
    password = request.form.get('password')
    error_message = check_login_form(email, password)
    if error_message:
        flash(error_message, category="error")
        return render_template('login.html', menu_url=fdb.get_menu(),  logged=logged)

    response = make_response(redirect(url_for("index")))
    response.set_cookie("logged", "yes")
    return response


@app.route("/signup", methods=["GET", "POST"])
@if_not_logged_in
def sign_up():
    logged = True if request.cookies.get("logged") else False
    if request.method == "GET":
        return render_template("signup.html", menu_url=fdb.get_menu(), logged=logged)

    email = request.form.get('email')
    password = request.form.get('password')
    password2 = request.form.get("password2")
    error_message = get_form_error_message(email, password, password2)
    if error_message:
        flash(error_message, category="error")
        return render_template("signup.html", menu_url=fdb.get_menu(), logged=logged)

    register_user(email, password)
    response = make_response(redirect(url_for("index")))
    response.set_cookie("logged", "yes")
    return response


@app.route("/logout")
@if_logged_in
def log_out():
    response = make_response(redirect(url_for("index")))
    response.delete_cookie("logged")
    return response


@app.errorhandler(404)
def page_not_found(error):
    return "<h1>This page doesn't exist!</h1>"


@app.teardown_appcontext
def close_db(error):
    """Close database connection if it exists."""
    if hasattr(g, 'link_db'):
        g.link_db.close()

def get_form_error_message(email: str, password: str, password2: str):
    if not (email and password and password2):
        return "All fields must be filled"

    required_symbols = ["@", "."]
    for symbol in required_symbols:
        if symbol not in email:
            return "Incorrect email address"

    if password != password2:
        return "Passwords don't match"

    if len(password) < 6 or password == password.lower():
        return "Password is too simple"

    is_email_used = FlaskDataBase(get_db()).is_email_exists(email)
    if is_email_used:
        return "User with this email has already been registered"

    return ""


if __name__ == '__main__':
    app.run(debug=True)
