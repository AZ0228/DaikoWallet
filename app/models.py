from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash #in the future put safeguards for security
from flask_login import UserMixin
from app import login
from hashlib import md5

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

#remove

class User(UserMixin, db.Model):
    id= db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64),index=True, unique = True)
    email = db.Column(db.String(120),index=True, unique = True)
    encrypted_password_hash = db.Column(db.String(128)) #encrypted password
    posts = db.relationship('Post', backref='author', lazy = 'dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    # take this out^^
    followed = db.relationship(
        'User', secondary=followers, 
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin = (followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic'
    )
    
    #add user details include demographics
    #monthly income and job and job description

    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        self.encrypted_password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.ecrypted_password_hash, password)
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)
    #----- dont need this
    def is_following(self,user):
        return self.followed.filter(followers.c.followed_id==user.id).count()>0
    
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
    
    def unfollow(self,user):
        if self.is_following(user):
            self.followed.remove(user)

    def followed_posts(self):
        return Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id).order_by(
                    Post.timestamp.desc())
    #-----------------
    def transaction(self):
        return Post.query.filter_by(user_id=self.id).order_by(Post.timestamp.desc())
    

    
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
    
    # add in option to look at demographics so that users can compare themselves to others
    

