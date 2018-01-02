from os import remove
from os.path import join
from flask import current_app, flash, redirect, url_for, session
from functools import wraps

def deleteFile(folder, filename):
    filename = folder + "/" + filename
    return remove(join(current_app.config['UPLOAD_FOLDER'], filename))

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("Unauthorized, Please login", 'danger')
            return redirect(url_for('dashboard.login'))
    return wrap


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
# Check the file
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
