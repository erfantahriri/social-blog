# from flask
from flask import jsonify

# from project
from .authentication import auth
from . import mod
from project.apps.auth.models import Comment, Post


@mod.route('/post/<int:id>/comments/')
@auth.login_required
def get_post_comments(id):
    post = Post.query.get_or_404(id)
    comments = post.comments
    return jsonify({'comments': [comment.to_json() for comment in comments]})


@mod.route('/comment/<int:id>')
@auth.login_required
def get_comment(id):
    comment = Comment.query.filter_by(id=id).first()
    return jsonify({'comment': comment.to_json()})