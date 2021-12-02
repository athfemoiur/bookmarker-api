from flask import Blueprint, request, jsonify
import validators

from constants.http_status_codes import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_201_CREATED, HTTP_200_OK, \
    HTTP_404_NOT_FOUND, HTTP_204_NO_CONTENT
from database import Bookmark, db
from flask_jwt_extended import jwt_required, get_jwt_identity

bookmark = Blueprint('bookmark', __name__, url_prefix='/api/bookmarks')


@bookmark.route('/', methods=['GET', 'POST'])
@jwt_required()
def create_list_bookmark():
    user_id = get_jwt_identity()
    if request.method == 'POST':

        body = request.get_json().get('body', '')
        url = request.get_json().get('url', '')

        if not validators.url(url):
            return jsonify({
                'error': 'Enter a valid url'
            }), HTTP_400_BAD_REQUEST

        if Bookmark.query.filter_by(url=url).first():
            return jsonify({
                'error': 'URL already exists'
            }), HTTP_409_CONFLICT

        bookmark_instance = Bookmark(url=url, body=body, user_id=user_id)
        db.session.add(bookmark_instance)
        db.session.commit()

        return jsonify({
            'id': bookmark_instance.id,
            'url': bookmark_instance.url,
            'short_url': bookmark_instance.short_url,
            'visit': bookmark_instance.visits,
            'body': bookmark_instance.body,
            'created_at': bookmark_instance.created_at,
            'updated_at': bookmark_instance.updated_at,
        }), HTTP_201_CREATED
    else:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)

        bookmarks = Bookmark.query.filter_by(
            user_id=user_id).paginate(page=page, per_page=per_page)

        data = []

        for bm in bookmarks.items:
            data.append({
                'id': bm.id,
                'url': bm.url,
                'short_url': bm.short_url,
                'visit': bm.visits,
                'body': bm.body,
                'created_at': bm.created_at,
                'updated_at': bm.updated_at,
            })

        meta = {
            "page": bookmarks.page,
            'pages': bookmarks.pages,
            'total_count': bookmarks.total,
            'prev_page': bookmarks.prev_num,
            'next_page': bookmarks.next_num,
            'has_next': bookmarks.has_next,
            'has_prev': bookmarks.has_prev,
        }

        return jsonify({'data': data, "meta": meta}), HTTP_200_OK


@bookmark.get("/<int:pk>/")
@jwt_required()
def get_bookmark(pk):
    current_user = get_jwt_identity()

    instance = Bookmark.query.filter_by(user_id=current_user, id=pk).first()

    if not bookmark:
        return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND

    return jsonify({
        'id': instance.id,
        'url': instance.url,
        'short_url': instance.short_url,
        'visit': instance.visits,
        'body': instance.body,
        'created_at': instance.created_at,
        'updated_at': instance.updated_at,
    }), HTTP_200_OK


@bookmark.route('/<int:pk>/', methods=['PUT', 'PATCH'])
@jwt_required()
def edit_bookmark(pk):
    current_user = get_jwt_identity()

    instance = Bookmark.query.filter_by(user_id=current_user, id=pk).first()

    if not bookmark:
        return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND

    body = request.get_json().get('body', '')
    url = request.get_json().get('url', '')

    if not validators.url(url):
        return jsonify({
            'error': 'Enter a valid url'
        }), HTTP_400_BAD_REQUEST

    instance.url = url
    instance.body = body

    db.session.commit()

    return jsonify({
        'id': instance.id,
        'url': instance.url,
        'short_url': instance.short_url,
        'visit': instance.visits,
        'body': instance.body,
        'created_at': instance.created_at,
        'updated_at': instance.updated_at,
    }), HTTP_200_OK


@bookmark.delete("/<int:id>/")
@jwt_required()
def delete_bookmark(pk):
    current_user = get_jwt_identity()

    instance = Bookmark.query.filter_by(user_id=current_user, id=pk).first()

    if not bookmark:
        return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND

    db.session.delete(instance)
    db.session.commit()

    return jsonify({}), HTTP_204_NO_CONTENT


@bookmark.get("/stats/")
@jwt_required()
def get_stats():
    current_user = get_jwt_identity()

    data = []

    items = Bookmark.query.filter_by(user_id=current_user).all()

    for item in items:
        new_link = {
            'visits': item.visits,
            'url': item.url,
            'id': item.id,
            'short_url': item.short_url,
        }

        data.append(new_link)

    return jsonify({'data': data}), HTTP_200_OK
