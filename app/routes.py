'''
routing file, manages all routes between pages/actions and database
'''

from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm, AddTransaction
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post, Friendship
from werkzeug.urls import url_parse
from datetime import datetime
import random

# function to get a random dashboard welcome message, feel free to adjust
def get_random_welcome_message(name):
    welcome_messages = [
        f"nice to see you, {name}!",
        f"welcome back, {name}!",
        f"hello, {name}! it's great to have you here.",
        f"glad you're here, {name}!",
        f"welcome, {name}!",
    ]
    return random.choice(welcome_messages)

# function to get the right date suffix Ex: june 2nd / june 4th
def convert_date(date):
    day = date.day
    suffix = 'th'
    if 4 <= day <= 20 or 24 <= day <=30: 
        pass
    else:
        suffixes = ['st', 'nd', 'rd']
        suffix = suffixes[day % 10 -1]
    return date.strftime(f'%B %d{suffix} %Y %#I:%M %P')

# route for the landing page
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html',title='Budget Buddy')

# route for the dashboard, methods include getting and posting data
@app.route('/dashboard', methods=['GET','POST'])
@login_required
def dashboard():
    expenses = current_user.transaction().all() # queries all user's transactions, see models.py for clarification
    message = get_random_welcome_message(current_user.username)
    form = AddTransaction() # add transaction form on the dashboard page, temporary just to test function, before spending page is designed
    if form.validate_on_submit(): 
        # need to replace this method with AJAX/server side processing so that there does not need to be a redirect-
        # every time transaction is changed/deleted
        # below is getting and setting form data
        amount = float(request.form.get('amount')) 
        necessity = bool(request.form.get('necessity'))
        post = Post(transaction_amount=amount,transaction_descript=form.description.data,
                     category=form.category.data,necessity=necessity, author=current_user,
                      transaction_timestamp = datetime.now() ) # creating a post with the queried data
        # adding and committing to database
        db.session.add(post)
        db.session.commit()
        flash('Your expense has been added!', 'success') 
        return redirect(url_for('dashboard'))
    # passes expenses, random message, and add transaction form
    return render_template('dashboard.html',title = 'dashboard', 
                           expenses = expenses, message = message, form=form)


# login route, methods include getting and posting data
@app.route('/login', methods=['GET','POST'])
def login():
    # if user is logged in already, redirect to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        # query form data
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data): # validates password, check models.py for more
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data) # login function from flask_login library
        next_page = request.args.get('next') # used in case user was redirected from some login-only feature
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('dashboard') #if no redirect, load the dashboard
        return redirect(next_page)
    return render_template('login.html', title = 'sign In', form = form)

# simple logout route using flask_login library
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# register form, methods include getting and posting data
@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated: #redirects to dashboard if already logged in
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit(): # user id and email is validated (no duplicates) in forms.py
        user = User(username=form.username.data, email=form.email.data) # creates new user object
        user.set_password(form.password.data)
        db.session.add(user) # updates database
        db.session.commit()
        flash('Congratualtions, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title = 'register', form = form)

# user profile page, might not be needed
@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    #passes in all of user's transactions, here for debugging purpose, enables anybody to see anybody else's full transaction history
    #------- remove later ----------------------------
    expenses = user.transaction().all()
    #-------------------------------------------------
    form = EmptyForm() #follow form, change to friend form
    return render_template('user.html',title = "user", user=user, expenses = expenses, form = form)

@app.route('/delete_expense/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    expense = Post.query.get_or_404(expense_id)
    db.session.delete(expense)
    db.session.commit()
    flash('post has been deleted')
    return redirect(url_for('dashboard'))


@app.route('/spending')
@login_required
def spending():
    return render_template('spending.html',title='spending')

@app.route('/send_friend_request/<int:user_id>/<int:friend_id>', methods=['GET','POST'])
def send_friend_request(user_id, friend_id):
    friendship = Friendship(user_id=user_id, friend_id=friend_id)
    db.session.add(friendship)
    db.session.commit()
    friend = User.query.filter_by(id=friend_id).first()
    return redirect(url_for('user',username = friend.username ))

#rewrite this to take both user ids instead
@app.route('/accept_friend_request/<int:user_id>/<int:friend_id>', methods=['GET','POST'])
def accept_friend_request(user_id, friend_id):
    friendship = Friendship.query.filter(
        (Friendship.user_id == user_id)&(Friendship.friend_id == friend_id) |
        (Friendship.user_id == friend_id)&(Friendship.friend_id == user_id)
        ).first()
    if friendship:
        friend = User.query.filter_by(id=friend_id).first()
        friendship.status = 'accepted'
        db.session.commit()
        return redirect(url_for('user',username = friend.username ))
        #'Friend request accepted successfully.'
    return 'Friend request not found.'

# needs implementation
@app.route('/unfriend/<int:user_id>/<int:friend_id>', methods=['GET','POST'])
def unfriend(user_id, friend_id):
    friendship = Friendship.query.filter(
        (Friendship.user_id == user_id)&(Friendship.friend_id == friend_id) |
        (Friendship.user_id == friend_id)&(Friendship.friend_id == user_id)
        ).first()
    if friendship:
        friend = User.query.filter_by(id=friend_id).first()
        db.session.delete(friendship)
        db.session.commit()
        return redirect(url_for('user',username = friend.username ))
    return 'Friend request not found.'

@app.route('/user/settings')
def settings():
    return 'hello'
