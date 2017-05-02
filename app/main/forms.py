# coding=utf-8
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired('用户名不能为空！'), Length(1, 64)])
    password = PasswordField('密码', validators=[DataRequired('密码不能为空！')])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')


class PostForm(FlaskForm):
    labels = StringField('Labels', validators=[DataRequired()])
    category = SelectField('Category', validators=[DataRequired()],
                           choices=[('前端', '前端'),
                                    ('后台', '后台'),
                                    ('机器学习', '机器学习'),
                                    ('数据分析', '数据分析')])
    title = StringField('Title', validators=[DataRequired()])
    body = TextAreaField('Body', validators=[DataRequired()])
    summery = TextAreaField('Summery', validators=[DataRequired()])
    submit = SubmitField('Submit')


class EditForm(FlaskForm):
    labels = StringField('Labels', validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired()])
    body = TextAreaField('Body', validators=[DataRequired()])
    summery = TextAreaField('Summery', validators=[DataRequired()])
    submit = SubmitField('Submit')


class CommentForm(FlaskForm):
    comment = TextAreaField('评论框(现仅仅支持MarkDown格式,互评和编辑器后续开发中)', validators=[DataRequired()])
    submit = SubmitField('Submit')