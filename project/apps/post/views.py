#from flask
from flask import Blueprint, render_template, abort, redirect, url_for, flash, current_app, request
from flask.ext.login import login_required, current_user

#from project
from project.apps.post.forms import PostForm, CommentForm
from project.extensions import db
from project.apps.auth.models import Permission
from project.apps.auth.models import Post, Comment


mod = Blueprint('post', __name__, url_prefix='/post')


@mod.route('/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data, post=post, author=current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been published.')
        return redirect(url_for('post.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) / current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'], error_out=False)
    comments = pagination.items
    return render_template('post/post.html', posts=[post], form=form, comments=comments, pagination=pagination, permission=Permission)


@mod.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash('The post has been updated.')
        return redirect(url_for('post.post', id=post.id))
    form.body.data = post.body
    return render_template('post/edit_post1.html', form=form, permission=Permission)


@mod.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(Permission.ADMINISTER):
        abort(403)

    db.session.delete(post)
    db.session.commit()

    flash('The post has been deleted.')
    return redirect(url_for('site.index'))
