import datetime
from flask import jsonify, make_response
from ..models import Blog, User
from .. import db
from .validation import NotFoundError, BusineesValidationError, BadRequest
from werkzeug.security import generate_password_hash
import pytz
from flask_restful import Resource, fields, marshal_with, reqparse


class MyDateFormat(fields.Raw):
    def format(self, value):
        return value.strftime("%d-%m-%Y %H:%M:%S")


output_user_fields = {
    "id": fields.Integer,
    "stored_profile_photo": fields.String,
    "stored_name": fields.String,
    "stored_bio": fields.String,
    "stored_email": fields.String,
    "stored_username": fields.String,
    "stored_timestamp": MyDateFormat
}

user_parser = reqparse.RequestParser()
user_parser.add_argument('input_name')
user_parser.add_argument('input_bio')
user_parser.add_argument('input_email')
user_parser.add_argument('input_username')
user_parser.add_argument('input_password')
user_parser.add_argument('input_confirm_password')



class UserAPI(Resource):
    # Get user
    @marshal_with(output_user_fields)
    def get(self, user_id = None):
        if not user_id:
            users = User.query.all()
            if users:
                return users
            else:
                return NotFoundError(error_message="No user present ")
        else:
            user = User.query.filter_by(id = user_id).first()
            if user:
                return user
            else:
                raise NotFoundError(error_message="User with user id " + str(user_id) +" is not present")

    @marshal_with(output_user_fields)
    def post(self):
        args = user_parser.parse_args()
        input_email = args.get("input_email", None)
        input_username = args.get("input_username", None)
        input_password = args.get("input_password", None)
        input_confirm_password = args.get("input_confirm_password", None)
        input_name = args.get("input_name")
        input_bio = args.get("input_bio")

        if not input_email:
            raise BusineesValidationError(error_message="Email cannot be empty")
        elif not input_username:
            raise BusineesValidationError(error_message="Username cannot be empty")
        elif not input_password:
            raise BusineesValidationError(error_message="Password cannot be empty")
        elif not input_confirm_password:
            raise BusineesValidationError(error_message="Confirm password cannot be empty")    

        email_exists = User.query.filter(User.stored_email==input_email).first()
        username_exists = User.query.filter(User.stored_username==input_username).first()

        if email_exists:
            raise BadRequest(error_message=input_email + " is already registered with us. Try to use different email")
        elif username_exists:
            raise BadRequest(error_message=input_username + " is already registered with us. Try to use different username")
        elif input_password != input_confirm_password:
            raise BadRequest(error_message='Passwords don\'t match! ')
        elif len(input_username) < 2:
            raise BadRequest(error_message='Username length should be atleast 2')
        elif len(input_password) < 6:
            raise BadRequest(error_message='Password length should be atleast 6')
        elif len(input_email) < 4:
            raise BadRequest(error_message='Email address is invalid')
        else:
            new_user = User(stored_name = input_name, stored_bio = input_bio, stored_email=input_email, stored_username=input_username, stored_password=generate_password_hash(input_password),stored_timestamp = datetime.datetime.now(pytz.timezone('Asia/Kolkata')) )
            db.session.add(new_user)
            db.session.commit()
            return new_user,201


    
    @marshal_with(output_user_fields)
    def put(self, user_id):

        user = User.query.filter_by(id = user_id).first()
        if not user:
            raise BadRequest(error_message="Please enter correct user id to update")

        args = user_parser.parse_args()
        input_email = args.get("input_email")
        input_username = args.get("input_username")
        input_name = args.get("input_name")
        input_bio = args.get("input_bio")

        if input_email == user.stored_email:
            raise BusineesValidationError(error_message="You are already using "+ input_email + " email. Update to another email")
        elif input_username == user.stored_username:
            raise BusineesValidationError(error_message="You are already using "+ input_username + " username. Update to another username")
        elif input_name == user.stored_name and user.stored_name != "":
            raise BusineesValidationError(error_message="You are already using "+ input_name + " name. Update to another name")
        elif input_bio == user.stored_bio and user.stored_bio != "":
            raise BusineesValidationError(error_message="You are already using "+ input_bio + " bio. Update to another bio")
        

        email_exists = User.query.filter(User.stored_email==input_email).first()
        username_exists = User.query.filter(User.stored_username==input_username).first()

        if email_exists:
            raise BadRequest(error_message=input_email + " is already registered with us. Try to use different email")
        elif username_exists:
            raise BadRequest(error_message=input_username + " is already registered with us. Try to use different username")
        elif len(input_username) < 2 and input_username:
            raise BadRequest(error_message='Username length should be atleast 2')
        elif len(input_email) < 4 and input_email:
            raise BadRequest(error_message='Email address is invalid')
        else:
            if input_email:
                user.stored_email = input_email
            if input_username:
                user.stored_username = input_username
            if input_name:
                user.stored_name = input_name
            if input_bio:
                user.stored_bio = input_bio
            db.session.commit()
            return user
    
    def delete(self, user_id):
        user = User.query.filter_by(id = user_id).first()
        if not user:
            raise BadRequest(error_message="Please enter correct user id to delete")
        else:
            blogs = Blog.query.filter(Blog.author == user_id).all()
            for blog in blogs:
                db.session.delete(blog)
            db.session.delete(user)
            db.session.commit()
        return make_response(jsonify({"message":"User with id " + str(user_id) + " successfully deleted"}),200)


    