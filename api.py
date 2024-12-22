from flask import Blueprint, jsonify, request, current_app
from flask_login import current_user, login_required
from models import db, Post, Tag, Favorite, post_tags
from datetime import datetime

api = Blueprint('api', __name__)

@api.route('/posts', methods=['GET'])
def get_posts():
    page = request.args.get('page', 1, type=int)
    per_page = 20  # 1ページあたりの表示件数
    
    # デバッグログ追加
    current_app.logger.debug(f"Fetching posts... Page: {page}, Per page: {per_page}")
    
    # 投稿の取得（ページネーション付き）
    posts = Post.query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # デバッグログ追加
    current_app.logger.debug(f"Found {posts.total} posts, Current page: {posts.page}, Pages: {posts.pages}")
    
    # レスポンスの整形
    posts_data = []
    for post in posts.items:
        post_data = {
            'id': post.id,
            'content': post.content,
            'url': post.url,
            'created_at': post.created_at.isoformat(),
            'favorite_count': post.favorite_count,
            'replies_count': post.replies.count(),
            'author': {
                'id': post.author.id,
                'name': post.author.name,
                'profile_pic': post.author.profile_pic
            },
            'tags': [tag.name for tag in post.tags],
            'is_own': current_user.is_authenticated and post.user_id == current_user.id,
            'is_favorited': current_user.is_authenticated and post in current_user.favorites
        }
        posts_data.append(post_data)
    
    return jsonify({
        'posts': posts_data,
        'has_next': posts.has_next,
        'total': posts.total,
        'current_page': posts.page,
        'pages': posts.pages
    })

@api.route('/posts', methods=['POST'])
@login_required
def create_post():
    data = request.get_json()
    
    # 必須フィールドの検証
    if not all(key in data for key in ['url', 'content']):
        return jsonify({'error': '必須フィールドが不足しています'}), 400
    
    try:
        # 投稿の作成
        post = Post(
            content=data['content'],
            url=data['url'],
            user_id=current_user.id,
            ip_address=request.remote_addr
        )
        
        # タグの処理
        if 'tags' in data:
            for tag_name in data['tags']:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                post.tags.append(tag)
        
        db.session.add(post)
        db.session.commit()
        
        return jsonify({
            'message': '投稿が作成されました',
            'post_id': post.id
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error creating post: {str(e)}")
        db.session.rollback()
        return jsonify({'error': '投稿の作成に失敗しました'}), 500

@api.route('/posts/<int:post_id>/favorite', methods=['POST'])
@login_required
def toggle_favorite(post_id):
    post = Post.query.get_or_404(post_id)
    
    try:
        is_favorited = post in current_user.favorites
        if is_favorited:
            current_user.favorites.remove(post)
            post.favorite_count -= 1
            action = 'removed'
        else:
            current_user.favorites.append(post)
            post.favorite_count += 1
            action = 'added'
        
        db.session.commit()
        
        return jsonify({
            'message': f'Favorite {action}',
            'action': action,
            'favorite_count': post.favorite_count
        })
        
    except Exception as e:
        current_app.logger.error(f"Error toggling favorite: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'お気に入りの更新に失敗しました'}), 500

@api.route('/posts/<int:post_id>', methods=['DELETE'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    if post.user_id != current_user.id:
        return jsonify({'error': '権限がありません'}), 403
    
    try:
        db.session.delete(post)
        db.session.commit()
        return jsonify({'message': '投稿が削除されました'})
        
    except Exception as e:
        current_app.logger.error(f"Error deleting post: {str(e)}")
        db.session.rollback()
        return jsonify({'error': '投稿の削除に失敗しました'}), 500

@api.route('/tags/popular', methods=['GET'])
def get_popular_tags():
    # 人気のタグを10個取得
    popular_tags = db.session.query(Tag, db.func.count(post_tags.c.post_id).label('post_count'))\
        .join(post_tags)\
        .group_by(Tag.id)\
        .order_by(db.desc('post_count'))\
        .limit(10)\
        .all()
    
    return jsonify([{
        'name': tag.name,
        'count': count
    } for tag, count in popular_tags])

@api.route('/posts/<int:post_id>/replies', methods=['POST'])
@login_required
def create_reply(post_id):
    parent_post = Post.query.get_or_404(post_id)
    data = request.get_json()
    
    if not data.get('content'):
        return jsonify({'error': '返信内容が必要です'}), 400
        
    try:
        reply = Post(
            content=data['content'],
            url=data.get('url', ''),
            user_id=current_user.id,
            reply_to_id=post_id,
            ip_address=request.remote_addr
        )
        
        db.session.add(reply)
        db.session.commit()
        
        return jsonify({
            'message': '返信が投稿されました',
            'reply_id': reply.id
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error creating reply: {str(e)}")
        db.session.rollback()
        return jsonify({'error': '返信の投稿に失敗しました'}), 500

@api.route('/posts/tag/<tag_name>')
def get_posts_by_tag(tag_name):
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    posts = Post.query.join(Post.tags).filter(Tag.name == tag_name)\
        .order_by(Post.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    posts_data = []
    for post in posts.items:
        post_data = {
            'id': post.id,
            'content': post.content,
            'url': post.url,
            'created_at': post.created_at.isoformat(),
            'favorite_count': post.favorite_count,
            'replies_count': post.replies.count(),
            'author': {
                'id': post.author.id,
                'name': post.author.name,
                'profile_pic': post.author.profile_pic
            },
            'tags': [tag.name for tag in post.tags],
            'is_own': current_user.is_authenticated and post.user_id == current_user.id,
            'is_favorited': current_user.is_authenticated and post in current_user.favorites
        }
        posts_data.append(post_data)
    
    return jsonify({
        'posts': posts_data,
        'has_next': posts.has_next,
        'total': posts.total,
        'current_page': posts.page,
        'pages': posts.pages
    })

@api.route('/posts/user/<int:user_id>')
def get_posts_by_user(user_id):
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    posts = Post.query.filter_by(user_id=user_id)\
        .order_by(Post.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    posts_data = []
    for post in posts.items:
        post_data = {
            'id': post.id,
            'content': post.content,
            'url': post.url,
            'created_at': post.created_at.isoformat(),
            'favorite_count': post.favorite_count,
            'replies_count': post.replies.count(),
            'author': {
                'id': post.author.id,
                'name': post.author.name,
                'profile_pic': post.author.profile_pic
            },
            'tags': [tag.name for tag in post.tags],
            'is_own': current_user.is_authenticated and post.user_id == current_user.id,
            'is_favorited': current_user.is_authenticated and post in current_user.favorites
        }
        posts_data.append(post_data)
    
    return jsonify({
        'posts': posts_data,
        'has_next': posts.has_next,
        'total': posts.total,
        'current_page': posts.page,
        'pages': posts.pages
    })

@api.route('/posts/<int:post_id>/replies')
def get_replies(post_id):
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    replies = Post.query.filter_by(reply_to_id=post_id)\
        .order_by(Post.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    replies_data = []
    for reply in replies.items:
        reply_data = {
            'id': reply.id,
            'content': reply.content,
            'url': reply.url,
            'created_at': reply.created_at.isoformat(),
            'favorite_count': reply.favorite_count,
            'replies_count': reply.replies.count(),
            'author': {
                'id': reply.author.id,
                'name': reply.author.name,
                'profile_pic': reply.author.profile_pic
            },
            'tags': [tag.name for tag in reply.tags],
            'is_own': current_user.is_authenticated and reply.user_id == current_user.id,
            'is_favorited': current_user.is_authenticated and reply in current_user.favorites
        }
        replies_data.append(reply_data)
    
    return jsonify({
        'replies': replies_data,
        'has_next': replies.has_next,
        'total': replies.total,
        'current_page': replies.page,
        'pages': replies.pages
    })

@api.route('/posts/favorites')
@login_required
def get_favorite_posts():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # ユーザーのお気に入り投稿を取得
    posts = Post.query.join(Favorite)\
        .filter(Favorite.user_id == current_user.id)\
        .order_by(Post.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    posts_data = []
    for post in posts.items:
        post_data = {
            'id': post.id,
            'content': post.content,
            'url': post.url,
            'created_at': post.created_at.isoformat(),
            'favorite_count': post.favorite_count,
            'replies_count': post.replies.count(),
            'author': {
                'id': post.author.id,
                'name': post.author.name,
                'profile_pic': post.author.profile_pic
            },
            'tags': [tag.name for tag in post.tags],
            'is_own': current_user.is_authenticated and post.user_id == current_user.id,
            'is_favorited': True  # お気に入り一覧なので必ずTrue
        }
        posts_data.append(post_data)
    
    return jsonify({
        'posts': posts_data,
        'has_next': posts.has_next,
        'total': posts.total,
        'current_page': posts.page,
        'pages': posts.pages
    })