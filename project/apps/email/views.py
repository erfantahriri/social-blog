#from flask
from flask import Blueprint, render_template
from flask.ext.mail import Message
from threading import Thread

#from project
from project.application import mail

mod = Blueprint('email', __name__, url_prefix='/email')


def send_async_email(app, msg):
    # with app.app_context():
    mail.send(msg)


def send_email(to, subject, template, **kwargs):
    msg = Message(subject, sender='erfan.tahriri1@gmail.com', recipients=[to])
    msg.body = render_template(template, **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    mail.send(msg)
    # thr = Thread(target=send_async_email, args=[app, msg])
    # thr.start()
    # return thr


# def send_email(to, subject, template, **kwargs):
#     msg = Message(subject, 'erfan.tahriri1@gmail.com', recipients=[to])
#     msg.body = render_template(template + '.txt', **kwargs)
#     msg.html = render_template(template + '.html', **kwargs)
#     thr = Thread(target=send_async_email, args=[app, msg])
#     thr.start()
#     return thr


# @mod.route('email/', methods=['GET', 'POST'])
# def email():
#     msg = Message('test subject', sender='erfan.tahriri@gmail.com', recipients=['erfan.tahriri@gmail.com'])
#     msg.body = 'text body'
#     msg.html = '<b>HTML</b> body'
#     with app.app_context():
#         mail.send(msg)
#
#     return render_template('email/email.html')


# def send_email(to, subject, template, **kwargs):
#     msg = Message('[Flasky]' + subject, 'Flasky Admin <erfan.tahriri@gmail.com>', recipients=[to])
#     msg.body = render_template(template + '.txt', **kwargs)
#     msg.html = render_template(template + '.html', **kwargs)
#     mail.send(msg)