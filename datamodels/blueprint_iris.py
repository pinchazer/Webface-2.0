from flask import Blueprint
from flask import render_template
from .form import IrisForm
from flask import request
import requests
from requests.exceptions import ConnectionError, ConnectTimeout
import random
import os
from flask import current_app
#from config import Configuration as conf

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
iris_model_path = os.path.join(THIS_FOLDER, 'static/model/iris_KNN')

iris = Blueprint('iris', __name__, template_folder='templates', static_folder='static')


#with open(iris_model_path, 'rb') as mdl:
#    iris_model = joblib.load(mdl)

def rand_val():
    _dict = {
        'sl': str(round(random.uniform(3, 9), 2)),
        'sw': str(round(random.uniform(1, 5.4), 2)),
        'pl': str(round(random.uniform(0.5, 7.9), 2)),
        'pw': str(round(random.uniform(0.05, 3.5), 2))
    }
    return _dict

text = 'This parameters corresponds to '

@iris.route('/', methods=['POST','GET'])
def index():
    form = IrisForm(request.form)
    response = ''
    if request.method == 'POST':
        if 'reset' in request.form:
            form.sl.data, form.sw.data, form.pl.data, form.pw.data = '', '', '', ''
        if 'rand' in request.form:
            param = rand_val()
            form.sl.data = param['sl']
            form.sw.data = param['sw']
            form.pl.data = param['pl']
            form.pw.data = param['pw']
        if 'submit' in request.form:
            if form.validate():
                X = list(map(float, [form.sl.data, form.sw.data, form.pl.data, form.pw.data]))
                try:
                    r = requests.post('http://{}:5001/iris/predict'
                                      .format(current_app.config["SERVER_ADDRESS"]), json={"features": X})
                    response = r.json()['p']
                except (ConnectionError, ConnectTimeout):
                    response = "Can't establish connection ;("
                #species = iris_model.predict(X)[0]
                #answer = text + species
    return render_template('iris.html', fields=form, answer=response)


