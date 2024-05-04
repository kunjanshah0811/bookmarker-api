from flask import Blueprint, jsonify, request
import jwt
import validators
from src.constants import http_status_codes
from src.database import Bookmark,db
from flask_jwt_extended import current_user, get_jwt_identity, jwt_required
from flasgger import swag_from


global bookmarks

bookmarks=Blueprint("bookmarks",__name__, url_prefix="/api/v1/bookmarks")


@bookmarks.route('/', methods=['POST','GET'])
@jwt_required()
def handle_bookmarks():
    
    current_user=get_jwt_identity()

    if request.method =='POST':

        body=request.get_json().get('body','')
        url =request.get_json().get('url','')

        if not validators.url(url):
            return jsonify({'error':'Enter a valid url'});HTTP_400_BAD_REQUEST

        if Bookmark.query.filter_by(url=url).first():
            return jsonify({'error':'URL already exists'}); HTTP_409_CONFLICT

        bookmark=Bookmark(url=url,body=body,user_id=current_user)
        db.session.add(bookmark)
        db.session.commit()

        return jsonify({
            'id':bookmark.id,
            'url':bookmark.url,
            'short_url':bookmark.short_url,
            'visit':bookmark.visits,
            'body':bookmark.body,
            'created_at':bookmark.created_at,
            'updated_at':bookmark.updated_at
        })

    else:
        
        book = Bookmark.query.filter_by(user_id=current_user).paginate(page =  page,per_page=per_page)
        data=[]
        page=request.args.get('page',1,type=int)
        per_page=request.args.get('per_page',5,type=int)
        

        for item in book.items:
            data.append({
            'id':item.id,
            'url':item.url,
            'short_url':item.short_url,
            'visit':item.visits,
            'body':item.body,
            'created_at':item.created_at,
            'updated_at':item.updated_at
            })

        meta={'page':book.page,
              'pages':book.pages,
              'total_count':book.total,
              'prev_page':book.per_page,
              'next_page':book.next_num,
              'has_next':book.has_next,
              'has_prev':book.has_prev,
              }

    return jsonify({'data':data,'meta':meta}),http_status_codes.HTTP_200_OK

@bookmarks.get("/<int:id>")
@jwt_required()
def get_bookmark(id):

    current_user=get_jwt_identity()

    bookmark=Bookmark.query.filter_by(user_id=current_user,id=id).first()

    if not bookmark:
        return jsonify({'error':"Item not found"});HTTP_404_NOT_FOUND

    return jsonify({
            'id':bookmark.id,
            'url':bookmark.url,
            'short_url':bookmark.short_url,
            'visit':bookmark.visits,
            'body':bookmark.body,
            'created_at':bookmark.created_at,
            'updated_at':bookmark.updated_at
        })

@bookmarks.put("/<int:id>")
@bookmarks.patch("/<int:id>")
@jwt_required()
def editbookmark(id):
    current_user=get_jwt_identity()

    bookmark=Bookmark.query.filter_by(user_id=current_user,id=id).first()

    if not bookmark:
        return jsonify({'error':"Item not found"});HTTP_404_NOT_FOUND

    body=request.get_json().get('body','')
    url =request.get_json().get('url','')

    if not validators.url(url):
            return jsonify({'error':'Enter a valid url'});HTTP_400_BAD_REQUEST    

    bookmark.url=url
    bookmark.body=body

    db.session.commit()

    return jsonify({
            'id':bookmark.id,
            'url':bookmark.url,
            'short_url':bookmark.short_url,
            'visit':bookmark.visits,
            'body':bookmark.body,
            'created_at':bookmark.created_at,
            'updated_at':bookmark.updated_at
        })

@bookmarks.delete("/<int:id>")
@jwt_required()
def delete_bookmark(id):
    current_user=get_jwt_identity()

    bookmark=Bookmark.query.filter_by(user_id=current_user,id=id).first()

    if not bookmark:
        return jsonify({'error':"Item not found"});HTTP_404_NOT_FOUND

    db.session.delete(bookmark)
    db.session.commit()

    return jsonify({})


@bookmarks.get("/stats")
@jwt_required()
@swag_from('./docs/bookmarks/stats.yaml')

def get_stats():
    data=[]
    current_user = get_jwt_identity()

    items=Bookmark.query.filter_by(user_id=current_user).all()

    for item in items:
        new_link={
            'visits':item.visits,
            'url':item.url,
            'id':item.id,
            'short_url':item.short_url
        }

        data.append(new_link)
        
    return jsonify({'data':data}); HTTP_200_OK


