#from flask
from flask import Blueprint, render_template, abort, redirect, flash, url_for, request, current_app
from flask.ext.login import login_required, current_user

#from project
from project.apps.profile.forms import EditProfileForm, EditProfileAdminForm
from project.extensions import db
from project.apps.decorators import admin_required, permission_required
from project.apps.auth.models import Permission, User_auth as User, Role_auth as Role, Post


mod = Blueprint('profile', __name__, url_prefix='/profile')


@mod.route('/<username>/')
def view_profile(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)

    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('profile/profile.html', user=user, posts=posts, permission=Permission, pagination=pagination)



@mod.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.family = form.family.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('profile.view_profile', username=current_user.username))
    form.name.data = current_user.name
    form.family.data = current_user.family
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('profile/edit_profile.html', form=form, user=current_user, permission=Permission)


@mod.route('/edit_profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.family = form.family.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated.')
        return redirect(url_for('profile.view_profile', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.family.data = user.family
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('profile/edit_profile_admin.html', form=form, user=user, permission=Permission)