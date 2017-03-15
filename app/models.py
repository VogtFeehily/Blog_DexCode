# coding=utf-8
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from markdown import markdown
from flask_login import UserMixin, AnonymousUserMixin
import bleach
from . import login_manager
from . import db


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

    @staticmethod
    # 运行后自动插入定义的 category
    def insert_category():
        categories = {
            '前端',
            '后台',
            '机器学习',
            '数据分析'
        }
        for c in categories:
            category = Category.query.filter_by(tag=c).first()
            if category is None:
                category = Category(tag=c, count=0)
                db.session.add(category)
                db.session.commit()


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
    
    '''
    @staticmethod
    # 创建假文章数据
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        for i in range(count):
            p = Post(title=forgery_py.lorem_ipsum.title(randint(1, 3)),
                     summery=forgery_py.lorem_ipsum.sentences(randint(20, 50)),
                     body=forgery_py.lorem_ipsum.sentences(randint(50, 100)),
                     category=Category.query.filter_by(id=randint(1, 4)).first(),
                     timestamp=forgery_py.date.date(True))
            db.session.add(p)
            db.session.commit()
    '''

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'blockquote', 'em', 'i', 'strong',
                        'li', 'ol', 'pre', 'strong', 'ul', 'h1', 'h2', 'h3', 'p', 'img']
        attrs = {
            '*': ['class'],
            'a': ['href', 'rel'],
            'img': ['src', 'alt']
        }
        target.body_html = bleach.linkify(bleach.clean(markdown(value, output_format='html'),
                                                       tags=allowed_tags, attributes=attrs, strip=True))

    @staticmethod
    def on_changed_summery(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'blockquote', 'em', 'i', 'strong',
                        'li', 'ol', 'pre', 'strong', 'ul', 'h1', 'h2', 'h3', 'p', 'img']
        attrs = {
            '*': ['class'],
            'a': ['href', 'rel'],
            'img': ['src', 'alt']
        }
        target.summery_html = bleach.linkify(bleach.clean(markdown(value, output_format='html'),
                                                          tags=allowed_tags, attributes=attrs, strip=True))

db.event.listen(Post.body, 'set', Post.on_changed_body)
db.event.listen(Post.summery, 'set', Post.on_changed_summery)


class Label(db.Model):
    __tablename__ = 'labels'
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(64), unique=True, index=True)
    count = db.Column(db.Integer, default=0)

    # 和Post是多对多的关系

    @staticmethod
    # 运行后自动插入定义的 label
    def insert_label():
        labels = {
            'Python',
            'Flask',
            'Java',
            'JSP',
            'Android',
            'HTML5',
            'JavaScript',
            'JQuery',
            'Ajax'
        }
        for l in labels:
            label = Label.query.filter_by(label=l).first()
            if label is None:
                label = Label(label=l, count=0)
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
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'blockquote', 'em', 'i', 'strong',
                        'li', 'ol', 'pre', 'strong', 'ul', 'h1', 'h2', 'h3', 'p', 'img']
        attrs = {
            '*': ['class'],
            'a': ['href', 'rel'],
            'img': ['src', 'alt']
        }
        target.comment_html = bleach.linkify(bleach.clean(markdown(value, output_format='html'),
                                                          tags=allowed_tags, attributes=attrs, strip=True))


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
