# coding=utf-8
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin

from . import login_manager
from . import db
from . import markdown


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128))
    comments = db.relationship('Comment', backref='user', lazy='dynamic')
    likes_post = db.relationship('LikePost', backref='user', lazy='dynamic')
    likes_comment = db.relationship('LikeComment', backref='user', lazy='dynamic')
    dislikes_comment = db.relationship('DislikeComment', backref='user', lazy='dynamic')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_dexter(self):
        return self is not None and self.username == 'Dexter' and self.id == 1

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
    @staticmethod
    def is_dexter():
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(64), unique=True, index=True)
    count = db.Column(db.Integer, default=0)
    posts = db.relationship('Post', backref='category', lazy='dynamic')


# Post 和 Label 的关联表
registrations = db.Table('registrations',
                         db.Column('post_id', db.Integer, db.ForeignKey('posts.id')),
                         db.Column('label_id', db.Integer, db.ForeignKey('labels.id')))


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    summery = db.Column(db.Text)
    summery_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    likes = db.relationship('LikePost', backref='post', lazy='dynamic')
    comment_num = db.Column(db.Integer, default=0)
    like_num = db.Column(db.Integer, default=0)
    labels = db.relationship('Label',
                             secondary=registrations,
                             backref=db.backref('posts', lazy='dynamic'),
                             lazy='dynamic')

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        target.body_html = markdown(value)

    @staticmethod
    def on_changed_summery(target, value, oldvalue, initiator):
        target.summery_html = markdown(value)

db.event.listen(Post.body, 'set', Post.on_changed_body)
db.event.listen(Post.summery, 'set', Post.on_changed_summery)


class Label(db.Model):
    __tablename__ = 'labels'
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(64), unique=True, index=True)
    count = db.Column(db.Integer, default=0)

    # 和Post是多对多的关系

    @staticmethod
    # 添加一个新的label
    def insert_label(lbl):
        label = Label.query.filter_by(label=lbl).first()
        if label is None:
            label = Label(label=lbl, count=0)
            db.session.add(label)
            db.session.commit()


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text)
    comment_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    # 评论者的UserID
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    like_num = db.Column(db.Integer, default=0)
    likes = db.relationship('LikeComment', backref='comment', lazy='dynamic')
    dislike_num = db.Column(db.Integer, default=0)
    dislikes = db.relationship('DislikeComment', backref='comment', lazy='dynamic')

    @staticmethod
    def on_changed_comment(target, value, oldvalue, initiator):
        target.comment_html = markdown(value)
db.event.listen(Comment.comment, 'set', Comment.on_changed_comment)


class LikePost(db.Model):
    __tablename__ = "like_post"
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class LikeComment(db.Model):
    __tablename__ = "like_comment"
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'))


class DislikeComment(db.Model):
    __tablename__ = "dislike_comment"
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
