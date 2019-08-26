from flask_wtf import FlaskForm
from ..models import User
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Regexp, EqualTo, Email, ValidationError


class Unique(object):
    def __init__(self, model, field, message=u'该用户已经存在。'):
        self.model = model
        self.field = field
        self.message = message
    
    def __call__(self, form, field):
        check = self.model.query.filter(self.field == field.data).first()
        if check:
            raise ValidationError(self.message)


class LoginForm(FlaskForm):
    email = StringField('邮箱', validators=[Required(), Length(1, 64),
                                          Email()])
    password = PasswordField('密码', validators=[Required()])
    remember_me = BooleanField('记住密码')
    submit = SubmitField('登陆')


class RegistrationForm(FlaskForm):
    email = StringField('邮箱', validators=[Unique(User, User.email, u"该邮箱已注册!"), Required(), Length(1, 64),
                                          Email()])
    username = StringField('用户名', validators=[Unique(User, User.username),
                                              Required(), Length(1, 64), Regexp('^[A-Za-z0-9_.]*$', 0,
                                                                                '用户名只能含有字母、数字和下划线')])
    password = PasswordField('请输入您的密码', validators=[
        Required(), EqualTo('password2', message='密码不匹配！')])
    password2 = PasswordField('请再次输入密码', validators=[Required()])
    submit = SubmitField('注册:-)')
