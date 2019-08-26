from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import Required, Length, ValidationError
from flask_pagedown.fields import PageDownField
from ..models import User


class Unique(object):
    def __init__(self, model, field, message=u'该用户已经存在。'):
        self.model = model
        self.field = field
        self.message = message
    
    def __call__(self, form, field):
        check = self.model.query.filter(self.field == field.data).first()
        if check and field.data != current_user.username:
            raise ValidationError(self.message)


class NoteSearchForm(FlaskForm):
    title = StringField('输入关键字搜索笔记')
    sumbit = SubmitField('笔记飞来~')


class EditProfileForm(FlaskForm):
    username = StringField('用户名', validators=[Unique(User, User.username), Length(0, 64)])
    about_me = TextAreaField('个性签名')
    submit = SubmitField('提交')


class PostForm(FlaskForm):
    body = PageDownField("说些什么吧~", validators=[Required()])
    # 启用markdown的文章表单
    submit = SubmitField('我说啦~')


class CommentForm(FlaskForm):
    body = StringField('说些什么吧', validators=[Required()])
    submit = SubmitField('我说啦~')
