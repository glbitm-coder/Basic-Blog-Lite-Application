from werkzeug.exceptions import HTTPException
from flask import make_response,jsonify


class NotFoundError(HTTPException):
    def __init__(self, error_message):
        message = {
            "error_message":error_message
        }
        self.response = make_response(jsonify(message), 404)

class BusineesValidationError(HTTPException):
    def __init__(self, error_message):
        message = {
            "error_message": error_message
            }
        self.response = make_response(jsonify(message), 409)

class BadRequest(HTTPException):
    def __init__(self, error_message):
        message = {
            "error_message":error_message
        }
        self.response = make_response(jsonify(message), 400)