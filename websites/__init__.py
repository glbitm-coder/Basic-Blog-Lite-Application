from flask import Flask, request, redirect
from flask import render_template
from os import path
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_restful import Resource, Api, fields, marshal_with, reqparse

db = SQLAlchemy()
DB_NAME = "blog_app.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "gveghwijlmrkb"
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    api = Api(app)

    from .views import view
    from .auth import auth
    from .all_api.user_api  import UserAPI
    from .all_api.blogs_api import BlogAPI


    app.register_blueprint(view, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    api.add_resource(UserAPI,"/api/user", "/api/user/<int:user_id>")
    api.add_resource(BlogAPI,"/api/user/<int:user_id>/blog", "/api/user/<int:user_id>/blog/<int:blog_id>", "/api/blog/<int:blog_id>")


    from .models import User, Blog, Comment, Like, Follow

    create_database(app)


    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists("websites/" + DB_NAME):
        with app.app_context():
            db.create_all()
        
