import os

from flask import Flask, redirect, jsonify

from constants.http_status_codes import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from src.auth import auth
from src.bookmark import bookmark
from src.database import db, Bookmark
from flask_jwt_extended import JWTManager


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('SQLALCHEMY_DB_URI'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY')
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    db.app = app
    db.init_app(app)
    JWTManager(app)
    app.register_blueprint(auth)
    app.register_blueprint(bookmark)

    @app.get('/<str:short_url>')
    def redirect_to_url(short_url):
        bookmark_instance = Bookmark.query.filter_by(short_url=short_url).first_or_404()

        if bookmark_instance:
            bookmark_instance.visits += 1
            db.session.commit()
            return redirect(bookmark_instance.url)

    @app.errorhandler(HTTP_404_NOT_FOUND)
    def handle_404(e):
        return jsonify({'error': 'Not found'}), HTTP_404_NOT_FOUND

    @app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
    def handle_500(e):
        return jsonify({'error': 'Something went wrong, we are working on it'}), HTTP_500_INTERNAL_SERVER_ERROR

    return app
