from flask import Blueprint
from flask import render_template, send_from_directory
from .form import UrlForm
from flask import current_app
from flask import request
import requests
from requests.exceptions import ConnectionError, ConnectTimeout
from PIL import Image, UnidentifiedImageError
import base64
from io import BytesIO
#from config import Configuration as conf
import os
import glob
from tempfile import NamedTemporaryFile

image_path = 'datamodels/gan_images'
gan = Blueprint('gan', __name__, template_folder='templates', static_folder='static')

def crop_and_resize(image):
    w, h = image.size
    if w / h >= 1.1:
        # image is not square shape like
        # album orientation
        return image.crop(((w - h) // 2, 0, (w + h) // 2, h)).resize((256, 256), resample=Image.LANCZOS)
    elif w / h <= 0.9:
        # image is not square shape like
        # portrait orientation
        return image.crop((0, (h - w) // 2, w, (h + w) // 2)).resize((256, 256), resample=Image.LANCZOS)
    elif 0.9 < w / h < 1.1:
        # image is square shape like
        return image.resize((256, 256), resample=Image.LANCZOS)


def save_image_to_file(image_b64_urlsafe):
    tf = NamedTemporaryFile(delete=False, suffix='.jpeg', prefix='gan_', dir=image_path)
    image = image_b64_urlsafe.replace("_", "/").replace("-", "+")
    image = f"{image}{'=' * ((4 - len(image) % 4) % 4)}"
    img_str_b = base64.b64decode(image)
    image = Image.open(BytesIO(img_str_b))
    image.save(tf, format='JPEG', quality=100)
    _, filename = os.path.split(tf.name)
    return filename

@gan.route('/', methods=['POST', 'GET'])
def index():
    form = UrlForm(request.form)
    new_image = 'empty.jpeg'
    answer = ''
    if request.method == 'POST' and form.validate():
        url = form.urlfld.data
        r = requests.get(url, stream=True)
        if r.ok:
            # here we check if it is an image source_image
            try:
                source_image = Image.open(r.raw)
                new_image = crop_and_resize(source_image)
                _b = BytesIO()
                if new_image.mode == 'RGBA':
                    background = Image.new("RGB", new_image.size, (255, 255, 255))
                    background.paste(new_image, mask=new_image.split()[3])  # 3 is the alpha channel
                    background.save(_b, format='JPEG', quality=100)
                else:
                    new_image.save(_b, format='JPEG', quality=100)
                img_str_b = base64.b64encode(_b.getvalue())
                _b.close()
                img_str = img_str_b.decode('ascii')
                r = requests.post('http://{}:8501/v1/models/cyclegan:predict'
                                  .format(current_app.config["SERVER_ADDRESS"]),
                                  json={"instances": [{"image": {"b64": img_str}}]})
                image_b64_urlsafe = r.json()['predictions'][0]
                new_image = save_image_to_file(image_b64_urlsafe)
            except UnidentifiedImageError:
                answer = 'Not a picture'
            except KeyError:
                answer = 'Tensorflow server respond: {}'.format(r.json())
            except OSError as e:
                answer = '{}'.format(e)
            except (ConnectionError, ConnectTimeout):
                answer = "Can't establish connection ;("
        else:
            answer = 'URL status_code {}'.format(r.status_code)
    return render_template('gan.html', answer=answer, image=new_image, form=form)

@gan.route('/images/<string:generated>', methods=['POST','GET'])
def show_image(generated):
    gan_images = glob.glob(os.path.abspath(os.path.join(image_path, 'gan_*')))
    if len(gan_images) >= 100:
        for f in gan_images[:-5]:
            os.remove(f)
    return send_from_directory(os.path.abspath(image_path), generated, mimetype='image/jpeg', cache_timeout=0)

