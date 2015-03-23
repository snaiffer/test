
#from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, IntegerField, Form
from wtforms.validators import Required

class LoginForm(Form):
  email_nickname = TextField('email_nickname', validators = [Required()])
  passwd = TextField('passwd', validators = [Required()])
  remember_me = BooleanField('remember_me', default = False)

class SignupForm(Form):
  email = TextField('email', validators = [Required()])
  nickname = TextField('nickname', default = '')
  passwd = TextField('passwd', validators = [Required()])
  passwd_chk = TextField('passwd_chk', validators = [Required()])

class SaveDataForm(Form):
  curtree_name = TextField('tree_name', default='')
  nestedocs = BooleanField('nestedocs', default = False)
  cmd = TextField('cmd', validators = [Required()])
  id = IntegerField('id', validators = [Required()])
  data = TextField('data', default = '')


