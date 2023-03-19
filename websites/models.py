from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
import datetime
import pytz

class Follow(db.Model):
    __tablename__ = 'follow'
    stored_follower_id = db.Column(db.Integer,db.ForeignKey('user.id',ondelete="CASCADE"), primary_key=True)
    stored_following_id = db.Column(db.Integer,db.ForeignKey('user.id',ondelete="CASCADE"), primary_key=True)

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    stored_profile_photo = db.Column(db.Text, default="/static/profile_photos/user_0_profile.jpg")
    stored_name = db.Column(db.String, default="")
    stored_bio = db.Column(db.Text, default="")
    stored_email = db.Column(db.String(64), unique=True)
    stored_username = db.Column(db.String(64), unique=True)
    stored_password = db.Column(db.String(64), unique=True)
    stored_timestamp = db.Column(db.DateTime(timezone=True))
    stored_blogs = db.relationship('Blog', backref='user', lazy='dynamic',cascade="all,delete")
    stored_comments = db.relationship('Comment', backref='user',cascade="all,delete" )
    stored_likes = db.relationship('Like', backref='user', cascade="all,delete")
    stored_followers = db.relationship('Follow',foreign_keys=[Follow.stored_following_id], backref='user',lazy='dynamic', cascade="all,delete")
    stored_following = db.relationship('Follow',foreign_keys=[Follow.stored_follower_id], backref='user2',lazy='dynamic', cascade="all,delete")


class Blog(db.Model):
    __tablename__ = 'blog'
    id = db.Column(db.Integer, primary_key=True)
    stored_title = db.Column(db.String(100), nullable=False)
    stored_caption = db.Column(db.Text, nullable=False)
    stored_url = db.Column(db.String(2048), default="",nullable=False)
    stored_timestamp = db.Column(db.DateTime(timezone=True))
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    stored_comments = db.relationship('Comment', backref='blog',cascade="all,delete")
    stored_likes = db.relationship('Like', backref='blog',  cascade="all,delete")

class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    stored_text = db.Column(db.String(180), nullable=False)
    stored_timestamp = db.Column(db.DateTime(timezone=True))
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id', ondelete="CASCADE"), nullable=False)


class Like(db.Model):
    __tablename__ = 'like'
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.Integer, db.ForeignKey('user.id',ondelete="CASCADE"), nullable=False)
    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id', ondelete="CASCADE"), nullable=False)

