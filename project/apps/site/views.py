#from flask
from flask import Blueprint, render_template, flash, redirect, url_for, request, current_app, make_response
from flask.ext.login import login_required, current_user
from flask.ext.sqlalchemy import get_debug_queries

#from project
from project.apps.site.forms import SiteForm
from project.apps.post.forms import PostForm
from project.apps.site.models import Site
from project.extensions import db
from project.apps.decorators import admin_required, permission_required
from project.apps.auth.models import Permission, User_auth as User, Follow, Post, Comment


mod = Blueprint('site', __name__, url_prefix='/')


@mod.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['FLASKY_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning('Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n' % (query.statement, query.parameters, query.duration, query.context))
    return response


@mod.route('setting/', methods=['GET', 'POST'])
def site_setting():
    form = SiteForm()

    if form.validate_on_submit():
        site_obj = Site()
        site_obj.title = form.title
        db.session.add(site_obj)
        db.commit()

    return render_template('site/setting.html', form=form)


@mod.route('moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
                        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
                        error_out=False)
    comments = pagination.items
    return render_template('site/moderate.html', comments=comments, pagination=pagination, page=page, permission=Permission)


@mod.route('moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('site.moderate', page=request.args.get('page', 1, type=int)))


@mod.route('moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('site.moderate', page=request.args.get('page', 1, type=int)))


@mod.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        user = current_user._get_current_object()
        post = Post(body=form.body.data, author=user)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('site.index'))

    show_followed = False
    if current_user.is_authenticated():
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query

    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(Post.timestamp.desc()).paginate(page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('site/index.html', form=form, posts=posts, permission=Permission, show_followed=show_followed, pagination=pagination)


@mod.route('all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('site.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp


@mod.route('followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('site.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp


@mod.route('gf', methods=['GET', 'POST'])
def gf():
    User.generate_fake(50)
    Post.generate_fake(100)
    Follow.generate_fake(400)
    Comment.generate_fake(400)
    flash('generating fake informations complete...')
    return redirect(url_for('site.index'))


@mod.route('follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('site.index'))
    if current_user.is_following(user):
        flash('You are already following this user.')
        return redirect(url_for('profile.view_profile', username=username))
    current_user.follow(user)
    flash('You are now following %s.' % username)
    return redirect(url_for('profile.view_profile', username=username))


@mod.route('unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('site.index'))
    if not current_user.is_following(user):
        flash("You are already don't following this user.")
        return redirect(url_for('profile.view_profile', username=username))
    current_user.unfollow(user)
    flash('You are now unfollow %s.' % username)
    return redirect(url_for('profile.view_profile', username=username))


@mod.route('followers/<username>')
@login_required
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('site.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
                 page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
                 error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp} for item in pagination.items]
    return render_template('profile/followers.html', user=user, title="Followers of",
                           endpoint='.followers', pagination=pagination,
                           follows=follows, permission=Permission)


@mod.route('followed_by/<username>')
@login_required
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('site.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
                 page, per_page=current_app.config['FLASKY_FOLLOWED_PER_PAGE'],
                 error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp} for item in pagination.items]
    return render_template('profile/followed_by.html', user=user, title="Followers of",
                           endpoint='.followers', pagination=pagination,
                           follows=follows, permission=Permission)


@mod.route('admin')
@login_required
@admin_required
def for_admins_only():
    return "For administrators!"


@mod.route('moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def for_moderators_only():
    return "For comment moderators!"


@mod.route('user')
@login_required
@permission_required(Permission.FOLLOW)
def for_users():
    return "For followers!"


@mod.route('any')
def for_any():
    return "For any!"

