#from wtforms import Form, StringField, TextAreaField, validators
from wtforms import StringField, TextAreaField, validators
from flask_wtf import FlaskForm

#valid = [validators.DataRequired(), validators.Regexp('[0-9.]+', message='Only numbers')]
valid_iris = [validators.Regexp('[0-9.]+', message='Only numbers')]
valid_text = [validators.DataRequired(), validators.length(max=200, message='200 symbols allowed')]
valid_url = [validators.URL(message='not valid URL', require_tld=True)]


class IrisForm(FlaskForm):
    sl = StringField('sepal_len', validators=valid_iris, render_kw={'placeholder': "Sepal Length", 'class': 'form-control'})
    sw = StringField('sepal_wid', validators=valid_iris, render_kw={'placeholder': "Sepal Width", 'class': 'form-control'})
    pl = StringField('petal_len', validators=valid_iris, render_kw={'placeholder': "Petal Length", 'class': 'form-control'})
    pw = StringField('petal_wid', validators=valid_iris, render_kw={'placeholder': "Petal Width", 'class': 'form-control'})

class TextForm(FlaskForm):
    txtfld = TextAreaField('TextArea', validators=valid_text, render_kw={'class': 'form-control'})

class UrlForm(FlaskForm):
    urlfld = StringField('URL', validators=valid_url, render_kw={'placeholder': "Paste URL here and press ENTER", 'class': 'form-control'})
