from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

##CREATE TABLE IN DB
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
#Line below only required once, when creating DB. 
# db.create_all()


@app.route('/')
def home():
    return render_template("index.html", logged_in=current_user.is_authenticated)


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if User.query.filter_by(email=request.form["email"]).first():
            flash("this email already registered")
            return redirect(url_for("register"))
        else:
            new_user = User(
                id=len(User.query.all())+1,
                email=request.form["email"],
                password=generate_password_hash(request.form["password"], method='pbkdf2:sha256', salt_length=10),
                name=request.form["name"],
            )
            db.session.add(new_user)
            db.session.commit()
            return render_template("secrets.html", name=new_user.name)
    return render_template("register.html",  logged_in=current_user.is_authenticated)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
# this load_user is to get the current_user
# current authenticate status can be retrieved by current_user.is_authenticated


@app.route('/login', methods=["POST", "GET"])
def login():
    error = None
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                print(current_user.is_authenticated)
                return redirect("secrets")
            else:
                flash("Your password is not correct")
                return redirect(url_for('login'))
        else:
            flash("User not existed")
            return redirect(url_for('login'))
    return render_template("login.html", logged_in=current_user.is_authenticated)


@app.route('/secrets')
@login_required
def secrets():
    return render_template("secrets.html", name=current_user.name, logged_in=True)


@app.route('/logout')
def logout():
    pass


@app.route('/download')
@login_required
def download():
    # https://flask.palletsprojects.com/en/2.0.x/api/#flask.send_from_directory
    # static in this context is the directory and filename is the path relative to that directory
    return send_from_directory('static', filename="files/cheat_sheet.pdf")



if __name__ == "__main__":
    app.run(debug=True)
