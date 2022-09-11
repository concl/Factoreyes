from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

from flask import Flask, render_template
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from werkzeug.utils import secure_filename
from wtforms import FileField, SubmitField, PasswordField, StringField, IntegerField
from wtforms.validators import InputRequired, Length, ValidationError, DataRequired, NumberRange
from flask_bcrypt import Bcrypt
import os

from PIL import Image
from PIL import ImageDraw
import torch
import easyocr
import numpy as np
import argparse
from pix2tex import cli
from model import func
from model import recursive_nn
import torch.nn as nn


def draw_boxes(image, bounds, color='yellow', width=2):
    draw = ImageDraw.Draw(image)
    for bound in bounds:
        p0, p1, p2, p3 = bound[0]
        draw.line([*p0, *p1, *p2, *p3, *p0], fill=color, width=width)
        print(bound[0])
    return image


def get_boxes(name, lang=None):
    if lang is None:
        lang = ["en"]

    reader = easyocr.Reader(lang)
    bounds = reader.readtext(name)

    what = 0
    thing = {(what := what + 1): bound[0] for bound in bounds}
    return thing


def take_input_and_make_image(input1, input2):

    parser = argparse.ArgumentParser(description='GUI arguments')
    parser.add_argument('-t', '--temperature', type=float, default=.2, help='Softmax sampling frequency')
    parser.add_argument('-c', '--config', type=str, default='settings/config.yaml', help='path to config file')
    parser.add_argument('-m', '--checkpoint', type=str, default='checkpoints/weights.pth', help='path to weights file')
    parser.add_argument('--no-cuda', action='store_true', help='Compute on CPU')
    parser.add_argument('--no-resize', action='store_true', help='Resize the image beforehand')
    parser.add_argument('--gnome', action='store_true', help='Use gnome-screenshot to capture screenshot')
    arguments = parser.parse_args()

    model = cli.LatexOCR(arguments)

    treeman = recursive_nn(embed_d=3, onehot=torch.tensor([[1., 0, 0], [0., 1, 0], [0., 0, 1]]))
    treeman.load_state_dict(torch.load("ball.pt"))
    boxes = get_boxes("static/files/input.png")
    im = Image.open("static/files/input.png")

    problems_to_update = {}

    thingy = np.array(im)
    # print(thingy)

    sigma = nn.Sigmoid()

    summing1 = 0
    summing2 = 0

    for i, box in boxes.items():
        try:
            print(box)
            problem = thingy[box[1][1]:box[2][1], box[0][0]:box[1][0]]

            latexs = model(Image.fromarray(problem))
            tree = func(latexs)
            out = treeman(tree)

            prob = float(sigma(out))
            problems_to_update[i] = prob

            summing1 += prob
            summing2 += (1 - prob)

            # if out > 0:
            #     thingy[box[1][1]:box[2][1], box[0][0]:box[1][0]:,1:3] -= np.int8(int(sigma(out) * 100))
            print(out)
            print(model(Image.fromarray(problem)))
        except:
            continue



    if summing1 > input1:

        for i in problems_to_update:
            if problems_to_update[i] > 0.5:
                box = boxes[i]
                thingy[box[1][1]:box[2][1], box[0][0]:box[1][0]:, 1:3] -= np.int8(int(problems_to_update[i] * 100))

    elif summing2 > input2:

        for i in problems_to_update:
            if problems_to_update[i] < 0.5:
                box = boxes[i]
                thingy[box[1][1]:box[2][1], box[0][0]:box[1][0]:, 1:3] -= np.int8(int(problems_to_update[i] * 100))

    output = Image.fromarray(thingy)
    output.save("static/files/output.png")


app = Flask(__name__)

app.config['UPLOADED_IMAGES_DEST'] = '/'
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
app.config['SQLAlchemy_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'hello'
app.config['UPLOAD_FOLDER'] = 'static/files'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class UploadFileForm(FlaskForm):
    file = FileField(validators=[InputRequired(), FileAllowed(['png'])])
    submit = SubmitField("Upload File")


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)


class RegisterForm(FlaskForm):
    username = StringField(validators=[
        InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[
        InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField(validators=[
        InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[
        InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')


@app.route("/", methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    setting = settingForm()
    form1 = UploadFileForm()

    hasUploaded = False

    if setting.validate_on_submit():
        session["input1"] = setting.input1.data
        session["input2"] = setting.input2.data


    if form1.validate_on_submit():
        file = form1.file.data
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'],
                               secure_filename("input.png")))
        take_input_and_make_image(session["input1"] - 1, session["input2"]-1)

        hasUploaded = True

    if hasUploaded:
        outputFile = os.path.join(app.config['UPLOAD_FOLDER'], 'output.png')
    else:
        outputFile = None

    user = ""
    if "user" in session and session["user"] is not None and current_user.is_authenticated:
        user = session["user"]
        return render_template("index2.html", form=form1, setting=setting,
                               username=session["user"], outputImage=outputFile)
    else:
        return render_template("index.html", form=form1,
                               setting=setting, outputImage=outputFile)


@app.route('/about')
def about():
    if "user" in session and session["user"] is not None and current_user.is_authenticated:
        return render_template("about2.html")
    else:
        return render_template("about.html")


class settingForm(FlaskForm):
    input1 = IntegerField("Input 1", validators=[DataRequired(), NumberRange(min=1, max=100)],
                          render_kw={"placeholder": 5})
    input2 = IntegerField("Input 2", validators=[DataRequired(), NumberRange(min=1, max=100)],
                          render_kw={"placeholder": 3})
    submit = SubmitField('Update')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                session['user'] = user.username
                login_user(user)
                return redirect(url_for('home'))
    return render_template("newLogin.html", form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    session.pop("user", None)
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template("register.html", form=form)


db.create_all()
app.run(debug=True)
# if __name__ == '__main__':
