import os
from flask import render_template, flash, redirect, session, url_for, request, g, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid
from forms import LoginForm
from models import User, Submission
from werkzeug import secure_filename
from style_grader_main import grader

app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = set(['cpp', 'h'])

@app.before_request
def before_request():
    g.user = current_user

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/',  methods = ['GET'])
@app.route('/index', methods = ['GET'])
@login_required
def index():
    user = g.user

    if request.method == 'POST':
        # Get the FileStorage instance from request
        file = request.files['file']
        filename = secure_filename(file.filename)
        # Render template with file info
        return render_template('file.html',
            filename = filename,
            type = file.content_type)
    return render_template('index.html',
        title = 'Home',
        user = user)

@app.route('/upload', methods=['POST'])
def upload():
    # Get the name of the uploaded files
    uploaded_files = request.files.getlist("file[]")
    filenames = []
    for file in uploaded_files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join("app/" + app.config['UPLOAD_FOLDER'], filename))
            filenames.append(filename)

    list_of_online_files = []
    for filename in filenames:
        online_file = os.path.join("app/" + app.config['UPLOAD_FOLDER'], filename)
        list_of_online_files.append(online_file)

    response = grader(list_of_online_files)
    if response != []:
        sub = Submission(user_id = g.user.id, passed_grader = False)
    else:
        sub =  Submission(umich_id = g.user.umich_id, user_id = g.user.id, passed_grader = True)

    db.session.add(sub)
    db.session.commit()

    return render_template('upload.html', filenames=filenames, errors = response )

@app.route('/uploads/<filename>')
def uploaded_file(filename):
 return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route('/login', methods = ['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for = ['nickname', 'email'])
    return render_template('login.html',
        title = 'Sign In',
        form = form,
        providers = app.config['OPENID_PROVIDERS'])


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        return redirect(url_for('login'))
    user = User.query.filter_by(email = resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        user = User(email = resp.email, passed_grader = 0)
        db.session.add(user)
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember = remember_me)
    return redirect(request.args.get('next') or url_for('index'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))