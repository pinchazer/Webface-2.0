#from wtforms import Form, StringField, TextAreaField, validators
from wtforms import StringField, TextAreaField, validators
from flask_wtf import FlaskForm

#valid = [validators.DataRequired(), validators.Regexp('[0-9.]+', message='Only numbers')]

# 'sl': str(round(random.uniform(3, 9), 2)),
# 'sw': str(round(random.uniform(1, 5.4), 2)),
# 'pl': str(round(random.uniform(0.5, 7.9), 2)),
# 'pw': str(round(random.uniform(0.05, 3.5), 2))


# valid_iris_sl = [validators.Regexp('[0-9.]+', message='Only numbers'),
#                  validators.NumberRange(min=2.9, max=9.1, message='From 2.9 to 9.1')]
# valid_iris_sw = [validators.Regexp('[0-9.]+', message='Only numbers'),
#                  validators.NumberRange(min=0.9, max=5.5, message='From 0.9 to 5.5')]
# valid_iris_pl = [validators.Regexp('[0-9.]+', message='Only numbers'),
#                  validators.NumberRange(min=0.3, max=8, message='From 0.3 to 8')]
# valid_iris_pw = [validators.Regexp('[0-9.]+', message='Only numbers'),
#                  validators.NumberRange(min=0.04, max=3.6, message='From 0.04 to 3.6')]

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
