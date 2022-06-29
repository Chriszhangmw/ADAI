from flask import Flask
from flask_sqlalchemy import SQLAlchemy

class Config:
    # DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:159@localhost/db_ad?utf8'
    SQLALCHEMY_TRACE_MODIFICATIONS = True


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

class Result(db.Model):
    __tablename__ = 'result'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255))
    year = db.Column(db.String(255))
    reason = db.Column(db.String(255))
    month = db.Column(db.String(255))
    day = db.Column(db.String(255))
    week = db.Column(db.String(255))
    city = db.Column(db.String(255))
    area = db.Column(db.String(255))
    street = db.Column(db.String(255))
    floor = db.Column(db.String(255))
    location = db.Column(db.String(255))
    immediate_memory = db.Column(db.String(255))
    compute = db.Column(db.String(255))
    late_memory = db.Column(db.String(255))
    name_pencil = db.Column(db.String(255))
    name_watch = db.Column(db.String(255))
    repeat = db.Column(db.String(255))

    sentence = db.Column(db.String(255))
    wink = db.Column(db.String(255))
    paper = db.Column(db.String(255))
    draw = db.Column(db.String(255))

    date = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    path = db.relationship('Path', backref='result', uselist=False)

class Path(db.Model):
    __tablename__ = 'path'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255))
    year = db.Column(db.String(255))
    reason = db.Column(db.String(255))
    month = db.Column(db.String(255))
    day = db.Column(db.String(255))
    week = db.Column(db.String(255))
    city = db.Column(db.String(255))
    area = db.Column(db.String(255))
    street = db.Column(db.String(255))
    floor = db.Column(db.String(255))
    location = db.Column(db.String(255))
    immediate_memory = db.Column(db.String(255))
    compute = db.Column(db.String(255))
    late_memory = db.Column(db.String(255))
    name_pencil = db.Column(db.String(255))
    name_watch = db.Column(db.String(255))
    repeat = db.Column(db.String(255))

    sentence = db.Column(db.String(255))
    wink = db.Column(db.String(255))
    paper = db.Column(db.String(255))
    draw = db.Column(db.String(255))

    result_id = db.Column(db.Integer, db.ForeignKey('result.id'))


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    birthday = db.Column(db.Date)

    results = db.relationship('Result', backref='user')

    def __repr__(self):
        return '<User %r>' % self.username

class AnswerConfigDB(db.Model):
    __tablename__ = 'answer_config'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    city = db.Column(db.String(255))
    area = db.Column(db.String(255))
    street = db.Column(db.String(255))
    floor = db.Column(db.String(255))
    location = db.Column(db.String(255))


if __name__ == '__main__':
    db.create_all()