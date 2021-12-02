from flask import Blueprint, request, jsonify

from constants.http_status_codes import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_201_CREATED, HTTP_200_OK, \
    HTTP_401_UNAUTHORIZED
from database import User, db
from werkzeug.security import generate_password_hash, check_password_hash
import validators
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity

auth = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth.post('/register/')
def register():
    username = request.json.get('username', '')
    email = request.json.get('email', '')
    password = request.json.get('password', '')

    if len(password) < 6:
        return jsonify({'error': "Password is too short"}), HTTP_400_BAD_REQUEST

    if len(username) < 3:
        return jsonify({'error': "User is too short"}), HTTP_400_BAD_REQUEST

    if not username.isalnum() or " " in username:
        return jsonify({'error': "Username should be alphanumeric, also no spaces"}), HTTP_400_BAD_REQUEST

    if not validators.email(email):
        return jsonify({'error': "Email is not valid"}), HTTP_400_BAD_REQUEST

    if User.query.filter_by(email=email).first() is not None:
        return jsonify({'error': "Email is taken"}), HTTP_409_CONFLICT

    if User.query.filter_by(username=username).first() is not None:
        return jsonify({'error': "username is taken"}), HTTP_409_CONFLICT

    pwd_hash = generate_password_hash(password)

    user = User(username=username, password=pwd_hash, email=email)
    db.session.add(user)
    db.session.commit()

    return jsonify({
        'message': "User created",
        'user': {
            'id': user.id, 'username': username, "email": email
        }

    }), HTTP_201_CREATED


@auth.post('/login/')
def login():
    email = request.json.get('email', '')
    password = request.json.get('password', '')

    user = User.query.filter_by(email=email).first()

    if user:

        if check_password_hash(user.password, password):
            refresh = create_refresh_token(identity=user.id)
            access = create_access_token(identity=user.id)

            return jsonify({
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'refresh': refresh,
                    'access': access,
                }

            }), HTTP_200_OK

    return jsonify({'error': 'wrong credentials'}), HTTP_401_UNAUTHORIZED


@auth.get("/user/")
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email
    }), HTTP_200_OK


@auth.get('/token/refresh/')
@jwt_required(refresh=True)
def refresh_users_token():
    identity = get_jwt_identity()  # user_id
    access = create_access_token(identity=identity)

    return jsonify({
        'access': access
    }), HTTP_200_OK
