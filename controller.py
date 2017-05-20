from flask import Flask, render_template, redirect, url_for, \
     request, flash, abort, session
import os, gc

from helpers import config
from helpers.db_connect import connect
from helpers.decorators import login_required
from helpers.funcs import *

from models import user
from models.image import Recognizer
from models.search import Search


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
app.secret_key = config.SECRET_KEY

# INDEX PAGE
@app.route('/')
def index():
    return render_template('index.html')

# UPLOAD DECORATOR
@app.route('/upload/', methods=['POST'])
def upload():
    try:
        image = None
        if request.files['img-file'].filename:
            image = request.files['img-file']
        elif request.files['img-camera'].filename:
            image = request.files['img-camera']
        elif request.form['img-url']:
            image = request.form['img-url']
        if image:
            if upload_file(image, image.filename, app.config['UPLOAD_FOLDER']):
                flash('Upload success')
                return redirect( url_for('search', img=image.filename) )
            else:
                flash('Could not upload {}'.format(image.filename))
        else:
            flash("Give us an image to work with.")
    except Exception as e:
        flash('ERROR: {}'.format(e))
    return redirect( url_for('index') )

# SEARCH PAGE
@app.route('/search/')
@app.route('/search/<img>')
@app.route('/search/<img>/<int:page>/')
def search(img=None, page=1):
    results = None
    if not img:
        return render_template('search.html', img=img, results=results)
    try:
        image_filename = os.path.join(config.UPLOAD_FOLDER, img)
        #r = Recognizer()
        #image_label = r.recognize(image_filename)     # Returns a string of image label
        image_label = 'victor'
        search = Search()
        results = search.search(image_label, page)
    except Exception as e:
        flash('ERROR: {}'.format(e))
    return render_template('search.html', img=img, page=page, results=results)

# REGISTER FUNCTION
@app.route('/register/', methods=['POST'])
def register():
    status = user.register(request.form['username'], request.form['password'],
                           request.form['confirm-password'])
    if status == user.SUCCESS:
        flash('Registration Successful!')
        return redirect( url_for('login') )
    return render_template('login.html', register_error=status)

# LOG IN PAGE
@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        status = user.login(request.form['username'], request.form['password'])
        if status == user.SUCCESS:
            flash('Login Successful!')
            return redirect( url_for('index') )
        return render_template('login.html', login_error=status)
    return render_template('login.html')

# LOGOUT PAGE
@app.route('/logout/')
@login_required
def logout():
    session.clear()
    gc.collect()
    return redirect( url_for('login') )

# SETTINGS PAGE
@app.route('/settings/')
def settings():
    return render_template('settings.html')

# HELP PAGE
@app.route('/help/')
def help():
    return render_template('help.html')

# ERROR HANDLER (404)
@app.errorhandler(404)
def page_not_found(e):
    make_dir(config.ERROR_DIR)
    create_file(config.ERROR_DIR + config.FOUR_OH_FOUR_ERR_FILE)
    errmsg = '{} – {}\n\t{}\n'.format(request.remote_addr, request.path, e)
    append_to_file(os.path.join(config.ERROR_DIR, config.FOUR_OH_FOUR_ERR_FILE), errmsg)
    return render_template('error/404.html', error=e)
