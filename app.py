from flask import (
    Flask, render_template, redirect,
    url_for, flash,request
)

from flask_login import (
    LoginManager, login_user, logout_user,
    login_required, current_user
)

from werkzeug.security import (
    generate_password_hash, check_password_hash
)

from forms import SignupForm, LoginForm, AdminLoginForm
from models import db, User, Company

from flask import Flask

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)
app.config["SECRET_KEY"] = "DSAISTOUGHBUTIMTOUGHER"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///placement.db"

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = SignupForm()

    if form.validate_on_submit():
        existing_user = User.query.filter(
    (User.username == form.username.data) |
    (User.usn == form.usn.data.strip().upper()) |
    (User.email == form.email.data.strip().lower())
).first()

        if existing_user:
            flash("Username or email already exists.", "danger")
        else:
            user = User(
    username=form.username.data,
    usn=form.usn.data.strip().upper(),
    email=form.email.data.strip().lower(),
    password_hash=generate_password_hash(form.password.data),
    role="student"
)

            db.session.add(user)
            db.session.commit()

            flash("Account created successfully. Please log in.", "success")
            return redirect(url_for("login"))

    return render_template("register.html", form=form)

 
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(
            usn=form.usn.data.strip().upper()
        ).first()

        if user and check_password_hash(
            user.password_hash, form.password.data
        ):
            if user.role == "student":
                login_user(user, remember=form.remember.data)
                flash("Student login successful.", "success")
                return redirect(url_for("placement_stats"))

            elif user.role == "senior":
                login_user(user, remember=form.remember.data)
                return redirect(url_for("senior_dashboard"))

            elif user.role == "admin":
                flash("Please use the admin login page.", "warning")

            else:
                flash("Your account role is not recognized.", "danger")

        else:
            flash("Invalid USN or password.", "danger")

    return render_template("login.html", form=form)



@app.route("/senior/dashboard")
@login_required
def senior_dashboard():
    if current_user.role != "senior":
        return "Forbidden", 403

    return render_template("senior/dashboard.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))

@app.route("/placement")
def placement_stats():
    search = request.args.get("company", "").strip()

    if search:
        companies = Company.query.filter(
            Company.name.ilike(f"%{search}%")
        ).order_by(Company.name).all()
    else:
        companies = Company.query.order_by(Company.name).all()

    return render_template(
        "placement.html",
        companies=companies
    )


@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    form = AdminLoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(
            username=form.username.data,
            role="admin"
        ).first()

        if user and check_password_hash(
            user.password_hash, form.password.data
        ):
            login_user(user)
            return redirect(url_for("home"))

        flash("Invalid admin credentials.", "danger")

    return render_template("admin-login.html", form=form)

if __name__ == "__main__":
    app.run(debug=True)