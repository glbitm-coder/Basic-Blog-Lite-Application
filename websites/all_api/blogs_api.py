import datetime
from flask import Blueprint, Flask, jsonify, make_response, request, redirect, url_for, flash
from flask import render_template
from ..models import Blog, User
from .. import db
from .validation import NotFoundError, BusineesValidationError, BadRequest
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import pytz
from flask_restful import Resource, Api, fields, marshal_with, reqparse


class MyDateFormat(fields.Raw):
    def format(self, value):
        return value.strftime("%d-%m-%Y %H:%M:%S")


output_blog_fields = {
    "id": fields.Integer,
    "stored_title" : fields.String,
    "stored_caption" : fields.String,
    "stored_timestamp" : MyDateFormat,
    "author" : fields.Integer 
}

blog_parser = reqparse.RequestParser()
blog_parser.add_argument('input_title')
blog_parser.add_argument('input_caption')

class BlogAPI(Resource):
    # Get user
    @marshal_with(output_blog_fields)
    def get(self, user_id = None, blog_id = None):
        if user_id is None:
            blog = Blog.query.filter_by(id = blog_id).first()
            if blog:
                return blog
            else:
                raise NotFoundError(error_message="Blog with blog id " + str(blog_id) + " is not present")
        else:
            user = User.query.filter_by(id = user_id).first()
            if user:
                if blog_id is None:
                    blogs = Blog.query.filter_by(author = user_id).all()
                    if blogs:
                        return blogs
                    else:
                        raise NotFoundError(error_message=" No blog present in " + user.stored_username + " profile")
                else:
                    blog = Blog.query.filter_by(id = blog_id, author = user_id).first()
                    if blog:
                        return blog
                    else:
                        raise NotFoundError(error_message="Blog with blog id " + str(blog_id) + " under user with id " + str(user_id) +" is not present")
            else:
                raise NotFoundError(error_message="User with user id " + str(user_id) +" is not present")

    @marshal_with(output_blog_fields)
    def post(self, user_id):
        user = User.query.filter_by(id = user_id).first()
        if not user:
            raise BadRequest(error_message="There is no user with id " + str(user_id))
        args = blog_parser.parse_args()
        input_title = args.get("input_title", None)
        input_caption = args.get("input_caption", None)

        if not input_title:
            raise BusineesValidationError(error_message="Title cannot be empty")
        elif not input_caption:
            raise BusineesValidationError(error_message="Caption cannot be empty")

        new_blog = Blog(stored_caption=input_caption, stored_title=input_title, author=user_id, stored_timestamp = datetime.datetime.now(pytz.timezone('Asia/Kolkata')))
        db.session.add(new_blog)
        db.session.commit()
        return new_blog,201


    
    @marshal_with(output_blog_fields)
    def put(self, user_id, blog_id):
        user = User.query.filter_by(id = user_id).first()
        if not user:
            raise BadRequest(error_message="There is no user with id " + str(user_id))
        blog = Blog.query.filter_by(id = blog_id, author = user_id).first()
        if not blog:
            raise BadRequest(error_message="There is no blog with id " + str(blog_id) + " under user with id " + str(user_id))

        args = blog_parser.parse_args()
        input_title = args.get("input_title", None)
        input_caption = args.get("input_caption", None)

        if not input_title:
            raise BusineesValidationError(error_message="Title cannot be empty")
        elif not input_caption:
            raise BusineesValidationError(error_message="Caption cannot be empty")

        if input_title == blog.stored_title:
            raise BusineesValidationError(error_message="You are already using "+ input_title + " title. Update to another title")
        elif input_caption == blog.stored_caption:
            raise BusineesValidationError(error_message="You are already using "+ input_caption + " caption. Update to another caption")

        blog.stored_title = input_title
        blog.stored_caption = input_caption
        
        db.session.commit()
        return blog
        
    
    def delete(self, user_id, blog_id):
        user = User.query.filter_by(id = user_id).first()
        blog = Blog.query.filter_by(id = blog_id, author = user_id).first()
        if not user:
            raise BadRequest(error_message="Please enter correct user id to delete")
        elif not blog:
            raise BadRequest(error_message="User with id " + str(user_id) + " doesn't contain blog with id " + str(blog_id))
        else:
            db.session.delete(blog)
            db.session.commit()
        return make_response(jsonify({"message":"Blog with id " + str(blog_id) + " successfully deleted"}),200)


    