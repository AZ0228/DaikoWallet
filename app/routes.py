from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm, AddTransaction
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post
from werkzeug.urls import url_parse
from datetime import datetime
import random

def get_random_welcome_message(name):
    welcome_messages = [
        f"nice to see you, {name}!",
        f"welcome back, {name}!",
        f"hello, {name}! it's great to have you here.",
        f"glad you're here, {name}!",
        f"welcome, {name}!",
    ]
    return random.choice(welcome_messages)

def convert_date(date):
    day = date.day
    suffix = 'th'
    if 4 <= day <= 20 or 24 <= day <=30: 
        pass
    else:
        suffixes = ['st', 'nd', 'rd']
        suffix = suffixes[day % 10 -1]
    return date.strftime(f'%B %d{suffix} %Y %#I:%M %P')

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html',title='Budget Buddy')

@app.route('/dashboard', methods=['GET','POST'])
@login_required
def dashboard():
    expenses = [
        {'type': {'price': "5.75"}, 'body': 'grocery store'},
        {'type': {'price': "6.00"}, 'body': 'thrift store'},
    ]
    expenses = current_user.transaction().all()
    message = get_random_welcome_message(current_user.username)
    form = AddTransaction()
    if form.validate_on_submit():
        amount = float(request.form.get('amount'))
        necessity = bool(request.form.get('necessity'))
        post = Post(transaction_amount=amount,transaction_descript=form.description.data,
                     category=form.category.data,necessity=necessity, author=current_user,
                      transaction_timestamp = datetime.now() )
        db.session.add(post)
        db.session.commit()
        flash('Your expense has been added!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('dashboard.html',title = 'Dashboard', 
                           expenses = expenses, message = message, form=form)


@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('dashboard')
        return redirect(next_page)
    return render_template('login.html', title = 'Sign In', form = form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratualtions, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title = 'Register', form = form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    expenses = user.transaction().all()
    form = EmptyForm()
    return render_template('user.html',title = "User", user=user, expenses = expenses, form = form)

@app.route('/delete_expense/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    expense = Post.query.get_or_404(expense_id)
    db.session.delete(expense)
    db.session.commit()
    flash('post has been deleted')
    return redirect(url_for('dashboard'))



#================================ probably won't need this =================================

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',form=form)

@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash('You are following {}!'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))

@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash('You are not following {}.'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))
#===========================================================================================

@app.route('/spending')
@login_required
def spending():
    return render_template('spending.html',title='spending')