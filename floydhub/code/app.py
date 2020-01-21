import os
from flask import Flask, send_file, request
from werkzeug.exceptions import BadRequest
from werkzeug.utils import secure_filename

import process

ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png'])
app = Flask(__name__)


@app.route('/', methods=["POST"])
def texturizer():
    """
    Take the input image and style transfer it
    """
    # check if the post request has the file part
    input_file = request.files.get('file')
    if not input_file:
        return BadRequest("File not present in request")

    filename = secure_filename(input_file.filename)
    if filename == '':
        return BadRequest("File name is not present in request")
    if not allowed_file(filename):
        return BadRequest("Invalid file type")

    os.mkdir('/images/')
    input_filepath = os.path.join('/images/', filename)
    output_filepath = os.path.join('/output/', filename)
    input_file.save(input_filepath)

    # Get checkpoint filename from la_muse
    process.process(input_filepath, output_filepath)
    return send_file(output_filepath, mimetype='image/jpg')


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == '__main__':
    app.run(host='0.0.0.0')
