from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import log
from .. import db
from ..models import User, Notebook
from .forms import LoginForm, RegistrationForm


@log.route('/login', methods=['GET', 'POST'])
def login():
    notebooks = Notebook.query.all()
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.private'))
        flash('错误的用户名或密码！')
    return render_template('log/login.html', form=form, notebooks=notebooks)


@log.route('/logout')
@login_required
def logout():
    logout_user()
    flash('你已退出登陆！')
    return redirect(url_for('main.private'))


@log.route('/register', methods=['GET', 'POST'])
def register():
    notebooks = Notebook.query.all()
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        flash('注册成功！')
        return redirect(url_for('log.login'))
    return render_template('log/register.html', form=form, notebooks=notebooks)


@log.before_app_request
# 更新已登录用户的访问时间
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
