
#from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, IntegerField, Form
from wtforms.validators import Required

class LoginForm(Form):
  username = TextField('username', validators = [Required()])
  passwd = TextField('passwd', validators = [Required()])
  remember_me = BooleanField('remember_me', default = False)

class RegistrationForm(Form):
  username = TextField('username', validators = [Required()])
  passwd = TextField('passwd', validators = [Required()])
  email = TextField('email', validators = [Required()])

class SaveDataForm(Form):
  curtree_id = IntegerField('tree_id', default=-1)
  nestedocs = BooleanField('nestedocs', default = False)
  cmd = TextField('cmd', validators = [Required()])
  id = IntegerField('id', validators = [Required()])
  data = TextField('data', default = '')


