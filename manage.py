import os

# 首字母大写都是类，小写都是对象
from app import create_app, db  # 从app/__init__.py中导入应用和数据库
from app.models import User, Role, Post, Notebook  # 从app.models（数据库模型）中导入用户和角色

app = create_app(os.getenv('FLASK_CONFIG') or 'default')  # 如果已经定义了环境变量flask_config，则从中读取配置，否则使用默认值

from flask import url_for
from flask_script import Manager, Shell

manager = Manager(app)  # Manger是一个管理类，manager为启动程序的对象

from flask_migrate import Migrate, MigrateCommand

migrate = Migrate(app, db)  # 数据库迁移对象


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Post=Post, Notebook=Notebook)


# 默认有runserver，我们增加了shell和db选项
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
# 该装饰器后的# 函数，可以用python manage.py [函数名] [函数参数] 运行一下函数
# 这里的参数aaa需要自己手动写，相比于上面的('db', MigrateCommand)的自动导入
def love(aaa):
    print("I love %s!" % aaa)


@manager.command
def standardize():
    user = User.query.filter_by(username='JWKR').first()
    notedir = os.path.abspath(os.path.dirname(__file__)) + '/notes'
    appdir = os.path.abspath(os.path.dirname(__file__)) + '/app/templates/notes'
    os.chdir(notedir)
    for each in os.listdir('.'):
        nowdir = notedir + '/' + each
        if os.path.isdir(nowdir):
            os.chdir(nowdir)
            if os.path.isdir(appdir + '/' + each) == False:
                os.mkdir(appdir + '/' + each)
            book = Notebook.query.filter_by(name=each).first()
            if book == None:
                book = Notebook(name=each)
                db.session.add(book)
                db.session.commit()
            for file in os.listdir('.'):
                div = file.split('.')
                if len(div) > 1 and (div[1] == 'html'):
                    with open(nowdir + '/' + file, "r", encoding="utf-8")as fin:
                        text = fin.readlines()
                        text[0] = """{% extends "base.html" %}\n"""
                        text[1] = """{% block title %}羽儿之家 - {{ title }}{% endblock %}\n"""
                        text[2] = """{% block head %}    {{ super() }}\n"""
                        for i in range(len(text)):
                            if text[i].split('\n')[0] == "</head>":
                                text[i] = """{% endblock %}{% block content %}\n"""
                        # text[-7] = """{% endblock %}{% block content %}\n"""
                        text[-1] = """{% endblock %}\n"""
                        with open(appdir + '/' + each + '/' + file, "w", encoding="utf-8") as fout:
                            fout.writelines(text)
                        note = Post.query.filter_by(title=div[0]).first()
                        if note == None:
                            body = "<a href=\"" + str(
                                url_for('notebook.note_html', bookname=each, notename=div[0])) + "\">" + div[0] + "</a>"
                            note = Post(title=div[0], body=body, author_id=user.id, notebook_id=book.id)
                            db.session.add(note)
                if file == 'README':
                    with open(nowdir + '/' + file, "r", encoding="utf-8")as fin:
                        text = fin.read()
                        book.descripton = text
                        db.session.add(book)
        db.session.commit()


@manager.command
def add_notes():
    user = User.query.filter_by(username='JWKR').first()
    notedir = os.path.abspath(os.path.dirname(__file__)) + '/notes'
    os.chdir(notedir)
    for each in os.listdir('.'):
        nowdir = notedir + '/' + each
        if os.path.isdir(nowdir):
            book = Notebook.query.filter_by(name=each).first()
            if book == None:
                book = Notebook(name=each)
                db.session.add(book)
                db.session.commit()
            os.chdir(nowdir)
            for file in os.listdir('.'):
                div = file.split('.')
                if len(div) > 1 and (div[1] == 'md'):
                    with open(nowdir + '/' + file, "r")as fin:
                        body = fin.read()
                        note = Post(title=div[0], body=body, author_id=user.id, notebook_id=book.id)
                        db.session.add(note)
                if file == 'README':
                    with open(nowdir + '/' + file, "r")as fin:
                        text = fin.read()
                        book.descripton = text
            db.session.add(book)
            db.session.commit()


@manager.command
def create_mysql():
    db.drop_all()
    db.create_all()


if __name__ == '__main__':
    manager.run()
