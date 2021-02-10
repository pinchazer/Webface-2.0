from flask import Blueprint
from flask import render_template
from .form import TextForm
from flask import request
import requests
from requests.exceptions import ConnectionError, ConnectTimeout
from flask import Markup
from config import Configuration as conf

text = Blueprint('text', __name__, template_folder='templates', static_folder='static')

@text.route('/', methods=['POST','GET'])
def index():
    form = TextForm(request.form)
    answer = ''
    if request.method == 'POST' and form.validate():
        try:
            r = requests.post('http://{}:5001/tweet/predict'.format(conf.SERVER_ADDRESS), json={"features": form.txtfld.data})
            answer = r.json()
            answer['answ'] = Markup(answer['answ'])
        except (ConnectionError, ConnectTimeout):
            answer = "Can't establish connection ;("
    return render_template('text.html', form=form, answer=answer)
