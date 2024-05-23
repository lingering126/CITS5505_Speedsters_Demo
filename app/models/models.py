from app import db
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import func
from enum import Enum

# Define the User model
class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    # new feature user profile pic
    profile_image_url = db.Column(db.String(200), default="/static/uploads/default_user.jpg")

    

# Define the LoginHistory model    
class LoginHistory(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    username = db.Column(db.String[64], index = True)
    login_time = db.Column(db.DateTime)
    logout_time = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('logins', lazy=True))
    

    def __repr__(self):
        return '<LoginHistory {}>'.format(self.id)



# Define the post model
class Post(db.Model):
    # Represents a post in the forum
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for the post
    title = db.Column(db.String(255), nullable=False)  # Title of the post, cannot be empty
    category = db.Column(db.String(255), nullable=True)
    content = db.Column(db.Text, nullable=False)  # Content of the post, cannot be empty
    created_at = db.Column(db.DateTime,default=datetime.utcnow)  # Record of when the post was created, defaults to current time
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('posts', lazy=True))

    # Track views and replies
    views = db.Column(db.Integer, default=0)
    replies_count = db.Column(db.Integer, default=0)

    # Date of last reply
    last_reply_date = db.Column(db.DateTime,default=datetime.utcnow)

    ####1.1 new feature likes
    likes = db.Column(db.Integer, default=0)
    #####1.1 new feature likes


    # Relationship to Reply model, a post can have many replies
    replies = db.relationship('Reply', backref='post', lazy='dynamic')

    # get latest reply time
    def get_last_reply_date(self):
        latest_reply = Reply.query.filter_by(post_id=self.id).order_by(Reply.created_at.desc()).first()
        if latest_reply:
            return latest_reply.created_at
        else:
            return self.created_at


# Defien the reply model
class Reply(db.Model):
    # Represents a reply to a post
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for the reply
    content = db.Column(db.Text, nullable=False)  # Content of the reply, cannot be empty
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)  # Foreign key to the post that this reply is associated with
    parent_id = db.Column(db.Integer, db.ForeignKey('reply.id'), nullable=True)  # Enables hierarchical structure for replies
    # Relationship for hierarchical replies; replies can have children and a parent
    children = db.relationship('Reply', backref=db.backref('parent', remote_side=[id]), lazy=True)
    created_at = db.Column(db.DateTime,default=datetime.utcnow)  # Record of when the reply was created, defaults to current UTC time
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('replies', lazy=True))

    ####1.1 new feature likes
    likes = db.Column(db.Integer, default=0)
    #####1.1 new feature likes


#######################################1.1 new feature
#Noification area
# Define Notification model
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # The user who will receive the notification
    actor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # The user who performed the action (mention/reply)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)  # The post where the action happened
    reply_id = db.Column(db.Integer, db.ForeignKey('reply.id'), nullable=True)  # The reply where the action happened
    message = db.Column(db.Text, nullable=False)  # The content of the mention/reply
    notification_type = db.Column(db.String(50), nullable=False)  # Type of notification (mention/reply)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('User', foreign_keys=[user_id])
    actor = db.relationship('User', foreign_keys=[actor_id])
    post = db.relationship('Post')
    reply = db.relationship('Reply')

########################################end of notification


#######################################1.1 new feature
# Define Vote model
class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)
    reply_id = db.Column(db.Integer, db.ForeignKey('reply.id'), nullable=True)
    vote_type = db.Column(db.String(10), nullable=False)  # 'like' or 'dislike'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('votes', lazy=True))
    post = db.relationship('Post', backref=db.backref('votes', lazy=True))
    reply = db.relationship('Reply', backref=db.backref('votes', lazy=True))
######################################1.1