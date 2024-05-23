from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from werkzeug.security import check_password_hash
from flask_login import current_user


# Form for updating profile picture
class UpdatePictureForm(FlaskForm):
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')]) # if format is incorrect, display a message
    submit_picture = SubmitField('Update Picture')

# Form for changing password
class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')]) # if password not match, display a message
    submit_password = SubmitField('Change Password')

