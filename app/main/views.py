# coding=utf-8
from flask import render_template, request, current_app, redirect, url_for, flash, jsonify
from flask_login import login_required, login_user, logout_user, current_user
from . import main
from .forms import PostForm, EditForm, CommentForm, LoginForm
from .. import db
from ..models import Category, Post, Label, Comment, User, LikePost
from ..decorators import dexter_required


@main.route('/', methods=['GET', 'POST'])
def index():
    categories = Category.query.all()
    labels = Label.query.all()
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    # 登录表单
    loginform = LoginForm()
    if loginform.validate_on_submit():
        user = User.query.filter_by(username=loginform.username.data).first()
        if user is not None and user.verify_password(loginform.password.data):
            login_user(user, loginform.remember_me.data)
            return redirect(url_for('main.index'))
        flash('用户不存在或者密码填写错误！')
    return render_template('index.html', posts=posts, pagination=pagination, loginform=loginform, categories=categories
                           , labels=labels)


@main.route('/category/<tag>', methods=['GET'])
def category(tag):
    categories = Category.query.all()
    category = Category.query.filter_by(tag=tag).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = category.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    # 登录表单
    loginform = LoginForm()
    if loginform.validate_on_submit():
        user = User.query.filter_by(username=loginform.username.data).first()
        if user is not None and user.verify_password(loginform.password.data):
            login_user(user, loginform.remember_me.data)
            return redirect(url_for('main.category', tag=tag))
        flash('用户不存在或者密码填写错误！')
    return render_template('category.html', category=category, posts=posts, pagination=pagination, loginform=loginform
                           , categories=categories)


@main.route('/write', methods=['GET', 'POST'])
@login_required
@dexter_required
def write():
    categories = Category.query.all()
    form = PostForm()
    loginform = LoginForm()
    if form.validate_on_submit():
        labels = []
        tag = form.category.data
        labels_article = form.labels.data.split(',')
        for l in labels_article:
            label = Label.query.filter_by(label=l).first()
            if label is None:
                label = Label(label=l, count=0)
                db.session.add(label)
                db.session.commit()
            labels.append(label)
        post = Post(title=form.title.data,
                    summery=form.summery.data,
                    body=form.body.data,
                    category=Category.query.filter_by(tag=tag).first(),
                    labels=labels,
                    comment_num=0,
                    like_num=0)
        # 增加一篇文章的同时将其所在的 Category 的文章数 +1
        post.category.count += 1
        db.session.add(post.category)
        db.session.commit()
        # 增加一篇文章的同时将其所包含的的 Label 的文章数 +1
        for label in labels:
            label.count += 1
            db.session.add(label)
            db.session.commit()
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.post', id=post.id))
    return render_template("write.html", form=form, loginform=loginform, categories=categories)


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@dexter_required
def edit(id):
    categories = Category.query.all()
    post = Post.query.get_or_404(id)
    form = EditForm()
    loginform = LoginForm()
    if form.validate_on_submit():
        labels = []
        labels_article = form.labels.data.split(',')
        for l in labels_article:
            label = Label.query.filter_by(label=l).first()
            if label is None:
                label = Label(label=l, count=0)
                db.session.add(label)
                db.session.commit()
            # 此时的 label 是 Label 对象
            labels.append(label)
        post.title = form.title.data
        post.summery = form.summery.data
        post.body = form.body.data
        # 在更新 post 的 label 之前先分出修改之前已经有的 Label 和修改后的 label
        # 这样在更新该 label 的文章数仅更新修改过的 Label 的文章数
        # 避免发生同一篇文章在一个 Label 上算成两篇甚至多篇文章这种情况
        # 1.修改文章时增加了 Label
        for label in labels:
            if label not in post.labels:
                label.count += 1
                db.session.add(label)
                db.session.commit()
        # 2.修改文章时删除了某些 Label
        # 遍历未修改之前的 Label
        for label in post.labels:
            if label not in labels:
                label.count -= 1
                db.session.add(label)
                db.session.commit()
        # 更新 post 的 label
        post.labels = labels
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.post', id=post.id))
    # 显示已有的信息
    form.title.data = post.title
    form.summery.data = post.summery
    form.body.data = post.body
    str = ''
    for label in post.labels:
        str += label.label
        str += ','
    form.labels.data = str
    return render_template("edit.html", form=form, category=post.category.tag, loginform=loginform
                           , categories=categories)


@main.route('/delete/<int:id>', methods=['GET'])
@login_required
@dexter_required
def delete_article(id):
    post = Post.query.get_or_404(id)
    # 删除一篇文章的同时将其所在的 Category 的文章数 -1
    post.category.count -= 1
    db.session.add(post.category)
    db.session.commit()
    # 删除一篇文章的同时将其所包含的 Label 的文章数 -1
    for label in post.labels:
        label.count -= 1
        db.session.add(label)
        db.session.commit()
    # 删除一篇文章的同时将其所有的 Comment
    for comment in post.comments:
        db.session.delete(comment)
        db.session.commit()
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('main.index'))


@main.route('/delete_comment/<int:id>', methods=['GET'])
@login_required
@dexter_required
def delete_comment(id):
    comment = Comment.query.get_or_404(id)
    # 保留comment 所在的 Post 的 id 方便重定向
    id = comment.post.id
    # 删除一个评论的同时将其所在的 Post 的评论数 -1
    comment.post.comment_num -= 1
    db.session.add(comment.post)
    db.session.commit()
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('main.post', id=id))


@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@main.route('/like_post')
@login_required
def like_post():
    # 通过 url 得到 post_id
    post_id = request.args.get('post_id', 0, type=int)
    post = Post.query.get_or_404(post_id)
    like_post = LikePost(post=post, user=current_user)
    db.session.add(like_post)
    db.session.commit()
    post.like_num += 1
    db.session.add(post)
    db.session.commit()
    return jsonify(likes=post.like_num)


@main.route('/undo_like_post')
@login_required
def undo_like_post():
    post_id = request.args.get('post_id', 0, type=int)
    post = Post.query.get_or_404(post_id)
    like_post = LikePost.query.filter_by(post=post, user=current_user)
    db.session.delete(like_post)
    db.session.commit()
    post.like_num -= 1
    db.session.add(post)
    db.session.commit()
    return jsonify(likes=post.like_num)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    categories = Category.query.all()
    form = CommentForm()
    loginform = LoginForm()
    post = Post.query.get_or_404(id)
    # 区别用户是否对该文章点赞
    like = False
    # 确定用户已经登陆在进行判断，否则为 False
    if current_user.is_authenticated:
        if LikePost.query.filter_by(post=post, user=current_user).first() is not None:
            like = True
    page = request.args.get('page', 1, type=int)
    pagination = post.comments.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['COMMENTS_PER_POST'], error_out=False)
    comments = pagination.items
    if form.validate_on_submit():
        comment = Comment(comment=form.comment.data, post=post, user=current_user)
        #  P增加一个评论的同时将评论所在的 post 的评论数 +1
        post.comment_num += 1
        db.session.add(post)
        db.session.commit()
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('main.post', id=id))
    # 登录表单
    if loginform.validate_on_submit():
        user = User.query.filter_by(username=loginform.username.data).first()
        if user is not None and user.verify_password(loginform.password.data):
            login_user(user, loginform.remember_me.data)
            return redirect(url_for('main.post', id=id))
        flash('用户不存在或者密码填写错误！')
    return render_template("post.html", post=post, form=form, comments=comments, pagination=pagination
                           , loginform=loginform, categories=categories, like=like)