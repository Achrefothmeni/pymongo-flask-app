from flask import Flask, render_template, redirect, request, url_for, session, flash, send_from_directory
from flask_pymongo import PyMongo
from pymongo import MongoClient
from werkzeug.utils import secure_filename
import os
from os.path import join, dirname, realpath

#Uploading folders Configurations
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static/uploads')

app = Flask(__name__)
app.secret_key = 'afh6x3dxj9d3xoi'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#app.config['MONGO_DBNAME'] = 'isgproj_db'
#app.config['MONGO_URI'] = 'mongodb://achrefothmeni:barcelona10@ds149138.mlab.com:49138/isgproj_db'

#Connecting to MongoDB
mongo = MongoClient('mongodb://achrefothmeni:barcelona10@ds149138.mlab.com:49138/isgproj_db')
db = mongo.isgproj_db

@app.route('/')
def index():
    return render_template('home.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/publish', methods=['GET','POST'])
def publish_events():
    if 'logged_in' not in session:
        return render_template('signup.html',err_log=True)
    else:
        if request.method == 'POST':
            title = request.form['title']
            description = request.form['description']
            club = request.form['club']
            place = request.form['place']
            price = request.form['price']
            date = request.form['date']
            file = request.files['file']
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            # if user does not select file, browser also
            # submit a empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                #return redirect(url_for('uploaded_file', filename=filename))
            event = db.events
            event.insert({'title':title, 'description':description, 'club':club, 'place':place, 'price':price,'date':date ,'image':file.filename})
            return redirect (url_for('events'))
        else:
            return render_template('publish-events.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)

@app.route('/events')
def events():
    events = db.events.find({})
    nb = events.count()
    return render_template('events.html', events=events, nb=nb)

@app.route('/signin', methods=['GET','POST'] )
def signin():
    if request.method == 'POST':
        user = db.users
        l_user = user.find_one({'username':request.form['username']})
        if l_user:
            if l_user['password'] == request.form['password']:
                session['username'] = request.form['username']
                session['logged_in'] = True
                return redirect (url_for('publish_events'))
            else:
                return render_template('login.html', err=True)
        else:
            return render_template('login.html', err=True)
    else:
        return render_template('login.html', err=False)

@app.route('/signup', methods=['GET','POST'] )
def signup():
    if request.method == 'POST':
        username = request.form['username']
        user = db.users
        existing_user = user.find_one({'username':username})
        if existing_user is None:
            user.insert({'username':username,'first_name':request.form['first_name'], 'last_name':request.form['last_name'], 'password': request.form['password']})
            return redirect(url_for('signin'))
        else:
            return render_template('signup.html', err=True)
    else:
        return render_template('signup.html', err=False)

@app.route('/signout')
def signout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('signin'))

if __name__ == '__main__':
    app.run(debug=True)



