# app.py
from flask import Flask, flash, Response, request, redirect, url_for, make_response, render_template
import json
import os
from werkzeug.utils import secure_filename
from src.img2gpx import img2gpx
import uuid

app = Flask(__name__)
app.secret_key = "djwoiu52983mc92m"


UPLOAD_FOLDER = 'img_upload/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

CONVERSION_FUNCTIONS = {'parkinson': img2gpx,
                        'weatherseed': img2gpx}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/retrieve/<method>/<filename>/<position>/<scale>/<algorithm>/<download_name>/")
def retrieve(method, filename, position, scale, algorithm, download_name=None):
    print("Retrieve: {}, {}, {}, {}, {}".format(method, filename, position, scale, download_name))
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    gpx_filename = filename.split('.')[0]
    pos = tuple([float(x) for x in position.split(',')])

    extra_args = {} # option to add various other args here

    gpx = CONVERSION_FUNCTIONS[algorithm](file_path, pos, float(scale), extra_args)

    if method=="GPX":
        return Response(gpx, mimetype='text/xml')
    elif method=="file":
        return Response(gpx,
                    mimetype="text/plain",
                    headers={"Content-Disposition":
                                 "attachment;filename={}.gpx".format(download_name)})


@app.route('/uploadajax', methods = ['POST'])
def upldfile():
    if request.method == 'POST':
        # file_val = request.files['file']

        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])

            # Generate unique filename
            save_name = uuid.uuid4().hex
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], save_name))

            resp = json.dumps({"filename": save_name,
                               "upload_name": filename})
            print('Returning ' + str(resp))

            return Response(resp, mimetype='application/json')


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')



if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)