from flask import render_template, abort, flash, redirect, url_for, request, current_app, session
from .forms import EditProfileForm, PostForm, CommentForm, NoteSearchForm, SubmitField, FlaskForm
from flask_login import login_required, current_user
from . import main
from ..models import User, Permission, Post, Comment, Notebook
from .. import db
from ..decorators import permission_required
from datetime import datetime, timedelta


@main.route('/', methods=['GET', 'POST'])
def index():
    notebooks = Notebook.query.all()
    search = NoteSearchForm()
    if search.validate_on_submit():
        return redirect(url_for('notebook.search', keywords=search.title.data))
    
    # 获取渲染的页数，无指定时回第一页
    page = request.args.get('page', 1, type=int)
    # 参数type=int保证参数无法转换成整数时,返回默认值
    posts = Post.query.filter(~Post.body.startswith('## 打卡')).order_by(Post.timestamp.desc())
    pagination = posts.paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    # page为必选参数，per_page显示每页显示的条数，值从程序的环境变量FLASKY_POSTS_PER_PAGE中获取
    posts = pagination.items
    return render_template('index.html', notebooks=notebooks, search=search, pagination=pagination, posts=posts)


@main.route('/user/<username>')
# 获取博客文章的资料页路由
def user(username):
    notebooks = Notebook.query.all()
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).filter_by(title=None).all()
    # 文章列表通过User.posts关系获取,User.posts返回的是查询对象
    # order_by()为过滤器
    return render_template('user.html', user=user, posts=posts, notebooks=notebooks)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    notebooks = Notebook.query.all()
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('你的资料已修改.')
        return redirect(url_for('.user', username=current_user.username))
    form.username.data = current_user.username
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form, notebooks=notebooks)


@main.route('/private', methods=['GET', 'POST'])
@login_required
def private():
    if current_user.username not in ["JWKR", "will131"]:
        return redirect(url_for('main.index'))
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        if form.body.data.startswith("睡觉"):
            body = "## 打卡" + form.body.data
        else:
            body = form.body.data
        if body.startswith("## 打卡"):
            flash("打卡成功")
        post = Post(body=body, author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.private'))
    # 获取渲染的页数，无指定时回第一页
    page = request.args.get('page', 1, type=int)  # 参数type=int保证参数无法转换成整数时,返回默认值
    posts = Post.query.filter(~Post.body.startswith('## 打卡')).order_by(Post.timestamp.desc())
    pagination = posts.paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    # page为必选参数，per_page显示每页显示的条数，值从程序的环境变量FLASKY_POSTS_PER_PAGE中获取
    posts = pagination.items
    return render_template('private.html', form=form, posts=posts,
                           pagination=pagination)


@main.route('/sleep')
@login_required
def sleep():
    if current_user.username not in ["JWKR", "will131"]:
        return redirect(url_for('main.index'))
    notebooks = Notebook.query.all()
    posts = Post.query.filter(Post.body.startswith('## 打卡睡觉')).order_by(Post.timestamp.asc())
    posts = [post for post in posts]
    index = 0
    time = datetime(2019, 1, 1, 16, 0)
    now = datetime.utcnow()
    day = []
    delta_time = []
    while time < now:
        while index < len(posts) and timedelta(hours=-12) > posts[index].timestamp - time:
            index += 1
        if index == len(posts):
            break
        if posts[index].timestamp - time < timedelta(hours=12):
            sleep_time = posts[index].timestamp
            index += 1
        else:
            sleep_time = time + timedelta(hours=2)
        day.append(time.strftime("%m-%d"))
        minutes = (sleep_time - time).seconds // 60
        if minutes > 1000:
            minutes -= 1440
        delta_time.append(minutes)
        time += timedelta(days=1)
    day_list = "["
    for each in day:
        day_list = day_list + "\'" + each + "\',"
    day_list = day_list[:-1] + "]"
    return render_template('detail.html', day=day_list, delta_time=delta_time)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
# 实例化了一个评论表单,并将其转入 post.html 模板
def post(id):
    notebooks = Notebook.query.all()
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        flash('评论成功！')
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) // \
               current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form,
                           comments=comments, pagination=pagination, notebooks=notebooks)


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    notebooks = Notebook.query.all()
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('moderate.html', comments=comments,
                           pagination=pagination, page=page, notebooks=notebooks)


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    notebooks = Notebook.query.all()
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))
