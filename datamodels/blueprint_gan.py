from flask import Blueprint
from flask import render_template, send_file
from .form import UrlForm
from flask import request
import requests
from requests.exceptions import ConnectionError, ConnectTimeout
from PIL import Image, UnidentifiedImageError
import base64
from flask import Markup
from io import BytesIO

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




@gan.route('/', methods=['POST', 'GET'])
def index():
    form = UrlForm(request.form)
    new_image = 'empty'
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
                r = requests.post('http://localhost:8501/v1/models/cyclegan:predict',
                                  json={"instances": [{"image": {"b64": img_str}}]})
                new_image = r.json()['predictions'][0]
            except UnidentifiedImageError:
                answer = 'Not a picture'
                new_image = 'empty'
            except KeyError:
                answer = 'Tensorflow server respond: {}'.format(r.json())
                new_image = 'empty'
            except OSError as e:
                answer = '{}'.format(e)
                new_image = 'empty'
            except (ConnectionError, ConnectTimeout):
                new_image = 'empty'
                answer = "Can't establish connection ;("
        else:
            answer = 'URL status_code {}'.format(r.status_code)
    return render_template('gan.html', answer=answer, image=new_image, form=form)

@gan.route('/show_image/<string:generated>.jpeg', methods=['POST','GET'])
def show_image(generated):
    _b = BytesIO()
    if generated == 'empty':
        # image = Image.new(mode='RGB', size=(1, 1), color=(255,255,255))
        image = Image.new(mode='RGB', size=(256, 256), color=(255, 255, 255))
        image.save(_b, format='JPEG', quality=100)
        _b.seek(0)
    else:
        image = generated.replace("_", "/").replace("-", "+")
        image = f"{image}{'=' * ((4 - len(image) % 4) % 4)}"
        img_str_b = base64.b64decode(image)
        image = Image.open(BytesIO(img_str_b))
        image.save(_b, format='JPEG', quality=100)
        _b.seek(0)
    return send_file(_b, mimetype='image/jpeg', cache_timeout=0)

#@gan.route('/show_image', methods=['POST','GET'])
#def show_image():
#    return 'show_image'
