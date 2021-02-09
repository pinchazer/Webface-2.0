from flask import Flask
from config import Configuration
from datamodels.blueprint_iris import iris
from datamodels.blueprint_text import text
from datamodels.blueprint_numbers import numbers
from datamodels.blueprint_gan import gan

app = Flask(__name__)
app.register_blueprint(iris, url_prefix='/iris')
app.register_blueprint(text, url_prefix='/text')
app.register_blueprint(numbers, url_prefix='/numbers')
app.register_blueprint(gan, url_prefix='/gan')
app.config.from_object(Configuration)






