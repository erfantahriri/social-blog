from project.extensions import db


class Site(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Unicode(255), unique=True, nullable=False)