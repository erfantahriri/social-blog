# from flask
from flask.ext.login import UserMixin, AnonymousUserMixin
from flask import current_app, url_for

# from system
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib
from markdown import markdown
import bleach

# from project
from project.extensions import db, ValidationError
from project.application import login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('user_auth.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    def to_json(self):
        json_post = {'url': url_for('api.get_comment', id=self.id, _external=True),
                     'body': self.body,
                     'body_html': self.body_html,
                     'timestamp': self.timestamp,
                     'disabled': self.disabled,
                     'author': url_for('api.get_user', id=self.author_id, _external=True),
                     'post_id': url_for('api.get_post', id=self.post_id, _external=True)}
        return json_post

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i', 'strong']
        target.body_html = bleach.linkify(bleach.clean(markdown(value, output_format='html'), tags=allowed_tags, strip=True))

    @staticmethod
    def generate_fake(count=200):
        from sqlalchemy.exc import IntegrityError
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User_auth.query.count()
        post_count = Post.query.count()
        for i in range(count):
            u = User_auth.query.offset(randint(0, user_count-1)).first()
            p = Post.query.offset(randint(0, post_count)).first()
            c = Comment(body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                        timestamp=forgery_py.date.date(True),
                        author_id=u.id,
                        post_id=p.id)
            db.session.add(c)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

db.event.listen(Comment.body, 'set', Comment.on_changed_body)


class Follow(db.Model):
    follower_id = db.Column(db.Integer, db.ForeignKey('user_auth.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('user_auth.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def generate_fake(count=200):
        from sqlalchemy.exc import IntegrityError
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User_auth.query.count()
        for i in range(count):
            u1 = User_auth.query.offset(randint(0, user_count-1)).first()
            u2 = User_auth.query.offset(randint(0, user_count-1)).first()
            if u1 != u2:
                f = Follow(follower_id=u1.id,
                           followed_id=u2.id,
                           timestamp=forgery_py.date.date(True))

                db.session.add(f)
                try:
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user_auth.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    def to_json(self):
        json_post = {'url': url_for('api.get_post', id=self.id, _external=True),
                     'body': self.body,
                     'body_html': self.body_html,
                     'timestamp': self.timestamp,
                     'author': url_for('api.get_user', id=self.author_id, _external=True),
                     'comments': url_for('api.get_post_comments', id=self.id, _external=True),
                     'comment_count': self.comments.count()}
        return json_post

    @staticmethod
    def from_json(json_post):
        body = json_post.get('body')
        if body is None or body == '':
            raise ValidationError('post does not have a body')
        return Post(body=body)

    @staticmethod
    def generate_fake(count=200):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User_auth.query.count()
        for i in range(count):
            u = User_auth.query.offset(randint(0, user_count - 1)).first()
            p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                     timestamp=forgery_py.date.date(True),
                     author=u)
            db.session.add(p)
            db.session.commit()

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
                           markdown(value, output_format='html'),
                                    tags=allowed_tags, strip=True))

db.event.listen(Post.body, 'set', Post.on_changed_body)


class User_auth(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    name = db.Column(db.String(64))
    family = db.Column(db.String(64))
    email = db.Column(db.String(64), unique=True, index=True)
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('role_auth.id'))
    registered_at = db.Column(db.DateTime(), default=datetime.utcnow)
    confirmed = db.Column(db.Boolean, default=False)
    role = db.relationship('Role_auth', foreign_keys='User_auth.role_id')
    avatar_hash = db.Column(db.String(32))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User_auth, self).__init__(**kwargs)
        if self.role_id is None:
            print self.email
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role_id = Role_auth.query.filter_by(permissions=0xff).first().id
            if self.role_id is None:
                self.role_id = Role_auth.query.filter_by(default=True).first().id
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()

    def to_json(self):
        json_user = {'url': url_for('api.get_user', id=self.id, _external=True),
                     'username': self.username,
                     'registered_at': self.registered_at,
                     'last_seen': self.last_seen,
                     'posts': url_for('api.get_user_posts', id=self.id, _external=True),
                     'followed_posts': url_for('api.get_user_followed_posts', id=self.id, _external=True),
                     'post_count': self.posts.count()}
        return json_user

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)
            db.session.commit()

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)
            db.session.commit()

    def is_following(self, user):
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        return self.followers.filter_by(follower_id=user.id).first() is not None

    def change_email(self, token):

        self.email = new_email
        self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        db.commit()
        return True

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url, hash=hash, size=size, default=default, rating=rating)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def can(self, permissions):
        return self.role is not None and (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @login_manager.user_loader
    def load_user(user_id):
        return User_auth.query.get(int(user_id))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id).filter(Follow.follower_id == self.id)

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    @staticmethod
    def generate_fake(count=200):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User_auth(email=forgery_py.internet.email_address(),
                          username=forgery_py.internet.user_name(True),
                          password=forgery_py.lorem_ipsum.word(),
                          confirmed=True,
                          name=forgery_py.name.first_name(),
                          family=forgery_py.name.last_name(),
                          location=forgery_py.address.city(),
                          about_me=forgery_py.lorem_ipsum.sentence(),
                          registered_at=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User_auth.query.get(data['id'])


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


class Role_auth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    user = db.relationship('User_auth', backref='role_auth', lazy='dynamic')


    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role_auth.query.filter_by(name=r).first()
            if role is None:
                role = Role_auth(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80





