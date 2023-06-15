'''
forms file, manages front end form templating and their connection to the backend
'''

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length, InputRequired
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    '''
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    '''
    submit = SubmitField('Register')

    def validate_username(self,username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username')
        
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address')

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args,**kwargs)
        self.original_username = original_username
    
    def validate_username(self, username):
        if username.data != self.original_username:
            user=User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Username is taken')

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')

#add option to attach receipt 
class AddTransaction(FlaskForm):
    amount = StringField('Amount', validators=[DataRequired()])
    category = SelectField('Expense Category', choices=[ #all different types of transactions
        ('housing', 'Housing'),
        ('transportation', 'Transportation'),
        ('food_groceries', 'Food and Groceries'),
        ('health_wellness', 'Health and Wellness'),
        ('entertainment', 'Entertainment'),
        ('personal_care', 'Personal Care'),
        ('education', 'Education'),
        ('debt_payments', 'Debt Payments'),
        ('savings_investments', 'Savings and Investments'),
        ('miscellaneous', 'Miscellaneous') # add other that can be customized by the user
    ], validators=[InputRequired()])
    necessity = SelectField('Necessity', choices=[('True','Needs'),('False','Wants')], validators = [InputRequired()])
    description = StringField('Description')
    submit = SubmitField('Submit')

class DeleteForm(FlaskForm):
    id_num = 0
    submit = SubmitField('Submit')
