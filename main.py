from flask import Flask, render_template, request, send_file, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
import pathlib
from flask_cors import CORS

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
# Use environment variable for secret in production
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')  # Required for flash messages

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'py', 'js', 'html', 'css', 'json'}

# Simple and safer check for allowed file extensions
def allowed_file(filename):
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS

# Configure CORS allowed origins via environment variable (comma separated)
allowed_origins_env = os.environ.get('ALLOWED_ORIGINS', 'http://localhost:5173,http://localhost:8080,https://localhostnotebook.netlify.app')
ALLOWED_ORIGINS = [o.strip() for o in allowed_origins_env.split(',') if o.strip()]
CORS(app, origins=ALLOWED_ORIGINS, supports_credentials=True)

def is_safe_path(basedir, path):
    # Prevent path traversal attacks
    return pathlib.Path(basedir).joinpath(path).resolve().is_relative_to(pathlib.Path(basedir).resolve())

@app.route('/')
def home():
    # Get list of uploaded files
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', files=files)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part in the request')
            return redirect(url_for('home'))
        
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(url_for('home'))
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            try:
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                flash(f'File "{filename}" uploaded successfully')
            except Exception as e:
                flash(f'Error saving file: {str(e)}')
            return redirect(url_for('home'))
        else:
            flash('File type not allowed')
            return redirect(url_for('home'))
    return redirect(url_for('home'))


@app.route('/download/<filename>')
def download_file(filename):
    try:
        if not allowed_file(filename):
            flash('File type not allowed for download')
            return redirect(url_for('home'))

        if not is_safe_path(app.config['UPLOAD_FOLDER'], filename):
            flash('Invalid filename')
            return redirect(url_for('home'))

        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(file_path):
            flash('File not found')
            return redirect(url_for('home'))

        return send_file(file_path, as_attachment=True)
    except Exception as e:
        flash(f'Error downloading file: {str(e)}')
        return redirect(url_for('home'))

@app.route('/delete/<filename>')
def delete_file(filename):
    try:
        if not allowed_file(filename):
            flash('File type not allowed for deletion')
            return redirect(url_for('home'))

        if not is_safe_path(app.config['UPLOAD_FOLDER'], filename):
            flash('Invalid filename')
            return redirect(url_for('home'))

        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            flash(f'File "{filename}" deleted successfully')
        else:
            flash('File not found')
    except Exception as e:
        flash(f'Error deleting file: {str(e)}')
    return redirect(url_for('home'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    debug_env = os.environ.get('FLASK_DEBUG', '0')
    debug = debug_env in ('1', 'true', 'True')
    app.run(host='0.0.0.0', port=port, debug=debug)
