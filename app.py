import os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from graph_worker import *

UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'txt', 'csv', 'xlsx'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.split('.')[-1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
           flash('No file part')
           return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            # проверяем содержимое файла
            filename = secure_filename(file.filename)
            # перед сохранением файла проверяем, есть ли там данные с предыдущих загрузок
            # если да - удаляем
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('graph'))
    return f'''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>'''

@app.route('/graph')
def graph():
    #
    files = os.listdir('static')
    #for file in 
    create_graph(
        [1, 2, 3, 4, 5],  # node ids
        ['Node #1', 'Node #2', 'Node #3', 'Node #4', 'Node #5'],  # node labels
        [(1, 2), (1, 3), (2, 3), (2, 4), (3, 5), (5, 5)],
        ['#d47415', '#22b512', '#42adf5', '#4a21b0', '#e627a3'], # node colors (HEX)
        r'templates/graph.html'
    )
    transform_graph_html(
        {'html_path':r'templates/graph.html',
            'utils_path':r'../static/scripts/utils.js',
            'network_js_path':r'../static/scripts/vis-network.min.js',
            'network_css_path':r'../static/styles/vis-network.css'}
    )
    return render_template('graph.html')

if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run(debug=True)
    # http://127.0.0.1:5000/