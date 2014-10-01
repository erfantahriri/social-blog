#from flask
from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask.ext.login import login_required, login_user, logout_user

#from project
from project.apps.auth.forms import LoginForm, AddRole, AddUser
from project.apps.auth.models import User_auth as User, Role_auth as Role, Permission
from project.extensions import db
from project.apps.email.views import send_email
from flask.ext.login import current_user

from flask import current_app

mod = Blueprint('auth', __name__, url_prefix='/auth')


@mod.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('site.index'))


@mod.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('dashboard.dashboard'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form, permission=Permission)


@mod.route('/add_user', methods=['GET', 'POST'])
def add_user():
    form = AddUser()

    if form.validate_on_submit():
        user_obj = User(username=form.username.data,
                        name=form.name.data,
                        family=form.family.data,
                        email=form.email.data,
                        password=form.password.data)
        db.session.add(user_obj)
        db.session.commit()

        token = user_obj.generate_confirmation_token()
        send_email(user_obj.email, 'Confirm Your Account', 'auth/email/confirm', user=user_obj, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('site.index'))
    return render_template('auth/add_user.html', form=form, permission=Permission)


@mod.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account', 'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('site.index'))


@mod.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        flash('Your account confirmed before!')
        return redirect(url_for('site.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!')

        user_obj = User.query.filter_by(name=current_user.name).first()
        user_obj.confirmed = '1'
        db.session.add(user_obj)
        db.session.commit()
        return redirect(url_for('auth.login'))

    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('site.index'))


@mod.before_app_request
def before_request():
    if current_user.is_authenticated():
        current_user.ping()
        if not current_user.confirmed and request.endpoint[:5] != 'auth.':
            return redirect(url_for('auth.unconfirmed'))


@mod.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous() or current_user.confirmed:
        return redirect('site.index')
    return render_template('auth/unconfirmed.html', permission=Permission)


@mod.route('/add_role', methods=['GET', 'POST'])
def add_role():
    Role.insert_roles()
    flash('Roles add')
    return redirect(url_for('site.index'))


#For Help:
# #from flask
# from flask import Blueprint, render_template
#
# #from project
# from project.apps.user.forms import Userform
# from project.apps.user.models import User
# from project.extensions import db
#
# mod = Blueprint('user', __name__, url_prefix='/user')
#
#
# @mod.route('/view/<username>', methods=['GET', 'POST'])
# def view(username):
#     form = Userform()
#     user_obj = User.query.filter_by(username=username).first()
#     if user_obj:
#         form.username.data = user_obj.username
#         form.password.data = user_obj.password
#         form.email.data = user_obj.email
#     else:
#         form.username.data = 'none'
#         form.password.data = 'none'
#         form.email.data = 'none'
#
#     return render_template('user/user.html', form=form)
#
#
# @mod.route('/add', methods=['GET', 'POST'])
# def add():
#     form = Userform()
#
#     if form.validate():
#         user_obj = User()
#         user_obj.username = form.username.data
#         user_obj.password = form.password.data
#         user_obj.email = form.email.data
#         db.session.add(user_obj)
#         db.session.commit()
#
#     return render_template('user/user.html', form=form)
#
#
# @mod.route('/delete/<username>')
# def delete(username=''):
#     user_obj = User.query.filter_by(username=username).first()
#     db.session.delete(user_obj)
#     db.session.commit()
#
#     return '%s DELETED !!!' %username
#
#
# @mod.route('/list', methods=['GET', 'POST'])
# def viewlist():
#     pass
#     form = Userform()
#     user_obj = User.query.all()
#
#     if user_obj:
#         form.username.data = ''
#         form.password.data = ''
#         form.email.data = ''
#
#         for item in user_obj:
#             form.username.data = ' '.join((form.username.data, item.username))
#             form.password.data = ' '.join((form.password.data, item.password))
#             form.email.data = ' '.join((form.email.data, item.email))
#     else:
#         form.username.data = 'none'
#         form.password.data = 'none'
#         form.email.data = 'none'
#
#     return render_template('user/user.html', form=form)
#
#
# @mod.route('/update/<username>', methods=['GET', 'POST'])
# def update(username=''):
#     form = Userform()
#     user_obj = User.query.filter_by(username=username).first()
#
#     if form.validate():
#         user_obj.username = form.username.data
#         user_obj.password = form.password.data
#         user_obj.email = form.email.data
#         db.session.add(user_obj)
#         db.session.commit()
#         return render_template('user/user.html', form=form)
#
#     form.username.data = user_obj.username
#     form.password.data = user_obj.password
#     form.email.data = user_obj.email
#     return render_template('user/user.html', form=form)