# app.py
from flask import Flask, flash, Response, request, redirect, url_for, make_response, render_template
app = Flask(__name__)
import json
import os
from werkzeug.utils import secure_filename
from src.img2gpx import img2gpx
import uuid

UPLOAD_FOLDER = 'img_upload/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/gpx/<filename>')
def gpx(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    gpx_filename = filename.split('.')[0]
    print(file_path)
    gpx = img2gpx(file_path)

    # response = make_response(gpx, 200)
    # response.mimetype = "text/plain"

    return Response(gpx, mimetype='text/xml')


@app.route('/download/<filename>/<upload_name>')
def download(filename, upload_name):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    gpx_filename = filename.split('.')[0]
    print(file_path)
    gpx = img2gpx(file_path)
    return Response(gpx,
                    mimetype="text/plain",
                    headers={"Content-Disposition":
                                 "attachment;filename={}.gpx".format(upload_name)})


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
    return render_template('view.html')



# @app.route('/uploads/<filename>')
# def uploaded_file(filename):
#     file_path = os.path.join(app.config['UPLOAD_FOLDER'],  filename)
#     gpx_filename = filename.split('.')[0]
#     print(file_path)
#     gpx = img2gpx(file_path)
#
#     # return Response(gpx, mimetype='text/xml')
#     return render_template('view.html', filename=filename)


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)