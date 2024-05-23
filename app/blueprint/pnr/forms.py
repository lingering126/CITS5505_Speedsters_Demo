# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    category = SelectField('Category', choices=[('news', 'News'),
        ('tutorial', 'Tutorial'),
        ('discussion', 'Discussion'),
        ('trade', 'Trade'),
        ('question', 'Question'),
        ('announcement', 'Announcement'),  
        ('event', 'Event'),  
        ('poll', 'Poll')],validators = [DataRequired()])
    submit = SubmitField('Create Post')

