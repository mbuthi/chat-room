from flask import Flask, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from dotenv import load_dotenv
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import declarative_base
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

from forms import RegisterForm, LoginForm, JobsForm

load_dotenv()
app = Flask(__name__)


app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", os.urandom(8))
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI")


bootstrap = Bootstrap5(app)

Base = declarative_base()

db = SQLAlchemy(app)

login_manager = LoginManager()

login_manager.init_app(app)

class Users(db.Model, UserMixin, Base):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    f_name = db.Column(db.String(20), nullable=False)
    l_name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    jobs = db.relationship("Jobs", backref="hiring_manager")
    applied_jobs = db.relationship("AppliedJobs", backref="employee")
class Jobs(db.Model, Base):
    __tablename__ = "jobs"
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.Text, nullable=False)
    category = db.Column(db.Text, nullable=False)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey("users.id"))
    applied = db.relationship("AppliedJobs", backref="applied")

class AppliedJobs(db.Model, Base):
    __tablename__ = "applied_jobs"
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))


with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)


@login_manager.unauthorized_handler
def unauthorized_handler():
    flash("Unauthorized", "error")
    return redirect(url_for('login'))
@app.route("/")
def home():
    return render_template("index.html")
@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user:
            flash("Email exists, login rather", "error")
            return redirect(url_for("login"))
        hash_password = generate_password_hash(password=form.password.data, 
        method="pbkdf2:sha256", salt_length=32)
        new_user = Users(f_name=form.f_name.data, l_name=form.l_name.data,
        email=form.email.data, password=hash_password)    
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash("Account created successfully", "success")
        return redirect(url_for("home"))
    return render_template("register.html", form=form)
@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if not user:
            flash("user does not exist, login rather", "error")
            return redirect(url_for("register"))
        if check_password_hash(password=form.password.data, pwhash=user.password):
            flash("login successfull", "success")
            return redirect(url_for("jobs"))
        flash("Incorrect password", "error")        
    return render_template("login.html", form=form)
@login_required
@app.route("/jobs")
def jobs():
    all_jobs = db.session.query(Jobs).all()  
    all_jobs_list = customFunction(all_jobs)
    return render_template("jobs.html", jobs=all_jobs_list)


@app.route("/add-jobs", methods=["POST", "GET"])
@login_required
def add_jobs():
    form = JobsForm()
    if form.validate_on_submit():
        new_job = Jobs(title=form.title.data.title(), category=form.category.data, public_id=str(uuid.uuid4()),
        description=form.description.data, hiring_manager=current_user)
        db.session.add(new_job)
        db.session.commit()
        flash("Job added successfully", "success")
        return redirect(url_for("add_jobs"))        
    return render_template("add-jobs.html", form=form)
@app.route("/apply", methods=["POST", "GET"])
@login_required
def apply_job():
    public_id = request.args.get("job")
    job = Jobs.query.filter_by(public_id=public_id).all()
    apply = AppliedJobs(applied=job[0], employee=current_user)    
    db.session.add(apply)
    db.session.commit()
    return redirect(url_for("jobs"))
@app.route("/profile", methods=["GET"])
@login_required
def profile():
    applied = Users.query.get(current_user.id).applied_jobs  
    posted = current_user.jobs      
    return render_template("profile.html", jobs=applied, posted=posted)
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))
@app.route("/jobs-category")
@login_required
def job_category():
    category = request.args.get("category")
    jobs = Jobs.query.filter_by(category=category).all()
    jobs = customFunction(jobs)
    return render_template("jobs.html", jobs=jobs)
# @app.route("/jobs/search")
# @login_required
# def search_jobs():

#     return render_template("jobs.html")
def customFunction(all_jobs):
    all_jobs_list = []      
    already_applied = current_user.applied_jobs
    ids_applied = []
    hires = []
    hiring = current_user.jobs
    for hire in hiring:
        hires.append(hire.id)
    for applied in already_applied:
        ids_applied.append(applied.job_id)
    for job in all_jobs:
        if not job.id in ids_applied and not job.id in hires:
            all_jobs_list.append(job)
    return all_jobs_list
