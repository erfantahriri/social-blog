# from flask
from flask import jsonify, request
from werkzeug.exceptions import BadRequest

# from project
from project.extensions import ValidationError
from . import mod


# @mod.route('/test/', methods=['POST'])
# def test():
#     username = request.form.get('username')
#     password = request.form.get('password')
#     test1 = request.form.get('test')
#
#     print username
#     print password
#     print test1
#
#     if username == 'erfan' and password == '123' and test1 == 'ali':
#         response = jsonify({'status': 100})
#     else:
#         response = jsonify({'status': 101})
#
#     return response
#
#
# @mod.route('/e/', methods=['POST'])
# def erfanjson():
#     name1 = request.form.get('name')
#     family1 = request.form.get('family')
#
#     if name1 == 'erfan' and family1 == 'tahriri':
#         response = jsonify({'status': 103})
#     else:
#         response = jsonify({'status': 104})
#
#     return response


def forbidden(message):
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response


@mod.errorhandler(ValidationError)
def validation_error(e):
    return BadRequest(e.args[0])