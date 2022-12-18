
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, EqualTo, Email
class RegisterForm(FlaskForm):
    f_name = StringField(label="First Name",validators=[DataRequired(),], render_kw={"placeholder":"Enter first name"})
    l_name = StringField(label="Last Name", validators=[DataRequired(),], render_kw={"placeholder":"Enter last name"})
    email = EmailField(label="Email", validators=[DataRequired(),Email(message="Not a valid email address")], render_kw={"placeholder": "Enter email address"})
    password = StringField(label="password", validators=[DataRequired(), EqualTo(fieldname="confirm_pass", message="password does not match")], render_kw={"placeholder":"Enter passsword"})
    confirm_pass = StringField(label="Confirm Password", validators=[DataRequired(),], render_kw={"placeholder": "Re-enter password"})
    submit = SubmitField(label="Register")

class LoginForm(FlaskForm):
    email = StringField(label="Email", validators=[DataRequired(), Email(message="Not a valid email address")], render_kw={"placeholder":"Enter email address"})
    password = StringField(label="password", validators=[DataRequired(),], render_kw={"placeholder": "Enter password"})
    submit = SubmitField(label="Login")

class JobsForm(FlaskForm):
    title = StringField(label="Job Title", validators=[DataRequired()])
    description = TextAreaField(label="Job Description", validators=[DataRequired()])
    category = SelectField(label="Job Category", validators=[DataRequired()], choices=["Design & Creative", "Development & IT", 
    "Sales & Marketing", "Writing & Translation", 
    "Admin & Customer Support", "Finance & Accounting",
    "Engineering & Architecture", "Legal"
    ])
    submit = SubmitField(label="Add Job")
