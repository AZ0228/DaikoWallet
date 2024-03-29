'''
models file, schema of the databases is stored/created through this file
'''
from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash # in the future put safeguards for security
from flask_login import UserMixin
from app import login
from hashlib import md5

# reloads user object from the user ID stored in the session
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# user model
class User(UserMixin, db.Model):
    id= db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64),index=True, unique = True)
    email = db.Column(db.String(120),index=True, unique = True)
    encrypted_password_hash = db.Column(db.String(128)) # encrypted password
    about_me = db.Column(db.String(140))
    posts = db.relationship('Post', backref='author', lazy = 'dynamic')
    notifs = db.relationship('Notification', backref='author', lazy='dynamic')
    # defining relationship between friendships and users, join conditions
    friendships = db.relationship(
        'Friendship',
        primaryjoin="or_(User.id == Friendship.user_id, User.id == Friendship.friend_id)",
        viewonly=True
    )
    # add user details include demographics
    # monthly income and job and job description

    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        self.encrypted_password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.encrypted_password_hash, password)
    
    def avatar(self, size): #randomly generated pfp, placeholder
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def friends_status(self, other_user):
        friendship = Friendship.query.filter(
            (Friendship.user_id == self.id)&(Friendship.friend_id == other_user.id) |
            (Friendship.user_id == other_user.id)&(Friendship.friend_id == self.id)
            ).first()
        if friendship is not None:
            # current user sent friend request, still pending
            if friendship.status == 'pending' and friendship.friend_id == self.id: 
                return 1
            # friend request is being sent to current user
            elif friendship.status == 'pending' and friendship.user_id == self.id:
                return 2
            else:
                return 3
        else:
            return 0

    def transaction(self):
        return Post.query.filter_by(user_id=self.id).order_by(Post.transaction_timestamp.desc())
    
    def notif(self):
        return Notification.query.filter_by(user_id=self.id).order_by(Notification.timestamp.desc())
    

    
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_amount = db.Column(db.Float)
    transaction_descript = db.Column(db.String(140))# details about the transaction, can be optional
    transaction_timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))# user that posted it
    category = db.Column(db.String(20))# types include: groceries? rent, clothes, etc.
    necessity = db.Column(db.Boolean)# is this purchase a need or a want

    def __repr__(self):
        return f'<Post {self.body}>'
    
    def convert_date(self):
        day = self.transaction_timestamp.day
        suffix = 'th'
        if 4 <= day <= 20 or 24 <= day <=30: 
            pass
        else:
            suffixes = ['st', 'nd', 'rd']
            suffix = suffixes[day % 10 -1]
        return self.transaction_timestamp.strftime(f'%#I:%M %P %B %d{suffix} %Y')
    
    # add in option to look at demographics so that users can compare themselves to others
    
class Friendship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    status = db.Column(db.String(20), nullable = False, default='pending')

class Notification(db.Model):
    id = db.Column(db.Integer,primary_key=True) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    message =  db.Column(db.String(50),nullable=False) #notification message
    timestamp = db.Column(db.DateTime,index=True, default = datetime.utcnow)
    other_user = db.Column(db.String(30), nullable=True)

    def getOtherUser(self):
        return User.query.filter_by(username = self.other_user)

    def convert_date(self):
        day = self.timestamp.day
        suffix = 'th'
        if 4 <= day <= 20 or 24 <= day <=30: 
            pass
        else:
            suffixes = ['st', 'nd', 'rd']
            suffix = suffixes[day % 10 -1]
        return self.timestamp.strftime(f'%#I:%M %P %B %d{suffix} %Y')

