from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from models import db, User

auth_bp = Blueprint(
    "auth",
    __name__
)


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return render_template(
                "auth/signup.html",
                error="Email already exists."
            )

        hashed_password = generate_password_hash(password)

        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_password,
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("auth.login"))

    return render_template("auth/signup.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):

            login_user(user)

            return redirect(url_for("dashboard.dashboard"))

        return render_template(
            "auth/login.html",
            error="Invalid email or password."
        )

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(url_for("auth.login"))