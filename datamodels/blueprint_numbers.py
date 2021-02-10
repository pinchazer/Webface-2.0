from flask import Blueprint
from flask import render_template
from flask import request
from .static.empty_image import empty_image
import base64
from PIL import Image
from io import BytesIO
import requests
import numpy as np
from requests.exceptions import ConnectionError, ConnectTimeout
from config import Configuration as conf

#THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
#numbers_model_path = os.path.join(THIS_FOLDER, 'static/model/numbers_model')


numbers = Blueprint('numbers', __name__, template_folder='templates', static_folder='static')


def coords(image):
    #up, right, down, left
    box = np.empty(shape=(4), dtype=np.int32)
    for i in range(image.shape[0]):
        if np.any(~image[i,:]): #row
            box[0] = i
            break
    for i in range(image.shape[0]):
        if np.any(~image[:,i]): #col
            box[1] = i
            break
    for i in range(image.shape[0]-1, -1, -1):
        if np.any(~image[i,:]): #row
            box[2] = i
            break
    for i in range(image.shape[0]-1, -1, -1):
        if np.any(~image[:,i]): #col
            box[3] = i
            break
    return box

def centralize(image):
    digit_c = image.convert('1')
    digit_arr = np.array(digit_c)
    box = coords(digit_arr)
    """
    0 | 1
    -----
    2 | 3

    0 = up, right = box[0], box[1]
    1 = up, left = box[0], box[3]
    2 = down, right = box[2], box[1]
    3 = down, left = box[2], box[3]
    """
    digit_width = box[3] - box[1]
    digit_height = box[2] - box[0]

    canvas_indent = int(digit_height / 5.0)
    canvas_size = digit_height + 2 * canvas_indent
    canvas = np.empty(shape=(canvas_size, canvas_size), dtype=np.bool)
    canvas.fill(True)

    _updown = (canvas_size - digit_height) / 2
    _rightleft = (canvas_size - digit_width) / 2

    _adder_down = 0
    _adder_up = 0
    _adder_left = 0
    _adder_right = 0

    up_canvas = np.floor(_updown)
    down_canvas = np.ceil(_updown)
    if up_canvas > down_canvas:
        _adder_down = 1
    elif up_canvas < down_canvas:
        _adder_up = 1
    right_canvas = np.floor(_rightleft)
    left_canvas = np.ceil(_rightleft)
    if right_canvas > left_canvas:
        _adder_left = 1
    elif right_canvas < left_canvas:
        _adder_right = 1

    box_canvas = np.array([up_canvas + _adder_up,
                           right_canvas + _adder_right,
                           down_canvas + digit_height + _adder_down,
                           left_canvas + digit_width + _adder_left],
                          dtype=np.int32)

    # print('canvas')
    # print('h: {}'.format(box_canvas[2] + _adder_down - box_canvas[0] + _adder_up))
    # print('w: {}'.format(box_canvas[3] + _adder_left - box_canvas[1] + _adder_right))
    # print('box')
    # print('h: {}'.format(box[2] - box[0]))
    # print('w: {}'.format(box[3] - box[1]))
    # print('\n')
    # print('canvas')
    # print('h: {}'.format(box_canvas[2] - box_canvas[0]))
    # print('w: {}'.format(box_canvas[3] - box_canvas[1]))
    # print('box')
    # print('h: {}'.format(box[2] - box[0]))
    # print('w: {}'.format(box[3] - box[1]))

    canvas[box_canvas[0]:box_canvas[2], box_canvas[1]:box_canvas[3]] = \
        digit_arr[box[0]:box[2], box[1]:box[3]]

    img = Image.fromarray((canvas * 255).astype('uint8'), 'L')

    return img


@numbers.route('/', methods=['GET'])
def index():
    return render_template('numbers.html')

@numbers.route('/draw', methods=['POST'])
def draw():
    answer = 'Empty picture'
    if request.method == 'POST':

        data_url = str(request.data) #request.data is bytes-like
        image_encoded = data_url.split(',')[1]
        image_encoded = image_encoded.encode('ascii')
        body = base64.decodebytes(image_encoded)
        _bio = BytesIO(body)
        img = Image.open(_bio)

        img.load()
        # make image opaque
        background = Image.new("RGB", img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3]) # 3 is the alpha channel
        _bio.close()
        try:
            img_centr = centralize(background)
        except Exception:
            img_centr = background
        img_resz = img_centr.resize((28, 28), resample=Image.BOX)

        _b = BytesIO()
        img_resz.save(_b, format='PNG', quality=100)
        img_str_b = base64.b64encode(_b.getvalue())
        _b.close()
        img_str = img_str_b.decode('ascii')

        if img_str != empty_image:
            try:
                r = requests.post('http://{}:8501/v1/models/mnist:predict'.format(conf.SERVER_ADDRESS),
                                  json={"instances": [{"image": {"b64": img_str}}]})
                a = r.json()['predictions'][0]
                if a['probabilities'] < 75:
                    answer = 'Seems like this is not a digit'
                else:
                    answer = 'You draw {}'.format(a['classes'])
            except (ConnectionError, ConnectTimeout):
                answer = "Can't establish connection ;("
        else:
            answer = 'Empty picture'
    return render_template('numbers.html', answer=answer)
