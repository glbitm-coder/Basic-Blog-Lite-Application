import datetime
from flask import Blueprint, Flask, request, redirect, url_for, flash
from flask import render_template
from . import db
from .models import User
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import pytz


auth = Blueprint('auth', __name__)


@auth.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        input_email = request.form.get("email")
        input_password = request.form.get("password")
        user = User.query.filter(User.stored_email==input_email).first()
        if user:
            if check_password_hash(user.stored_password, input_password):
                flash("Logged in!", category='success')
                login_user(user, remember=True)
                return redirect(url_for("home_views.profile"))
            else:
                flash("Password is incorrect!", category='error')
        else:
            flash('Email does not exist!', category='error')
    return render_template('login.html', user=current_user)

@auth.route('/sign-out')
@login_required
def sign_out():
    logout_user()
    return redirect("/login")

@auth.route("/sign-up", methods=['GET', 'POST'])
def sign_up():
    if request.method == "POST":
        input_email = request.form.get("email")
        input_username = request.form.get("username")
        input_password = request.form.get("password")
        input_confirm_password = request.form.get("confirm_password")

        email_exists = User.query.filter(User.stored_email==input_email).first()
        username_exists = User.query.filter(User.stored_username==input_username).first()
        
        if email_exists:
            flash('Email is already registered with us. Try to login', category='error')
        elif username_exists:
            flash('Username is already registered with us. Try to use different username', category='error')
        elif input_password != input_confirm_password:
            flash('Password don\'t match! ', category='error')
        elif len(input_username) < 2:
            flash('Username length should be atleast 2', category='error')
        elif len(input_password) < 6:
            flash('Password length should be atleast 6', category='error')
        elif len(input_email) < 4:
            flash('Email address is invalid', category='error')
        else:
            new_user = User(stored_email=input_email, stored_username=input_username, stored_password=generate_password_hash(input_password),stored_timestamp = datetime.datetime.now(pytz.timezone('Asia/Kolkata')) )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('User account has been successfully created')
            return redirect(url_for('home_views.profile'))
    return render_template('sign-up.html',user=current_user)


