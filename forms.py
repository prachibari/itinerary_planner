# -*- coding: utf-8 -*-
"""
Created on Sat Jan 26 22:23:47 2019

@author: Prachi
"""

from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,BooleanField
from wtforms.validators import Length,Email,DataRequired,EqualTo


class RegistrationForm(FlaskForm):
    fname = StringField('First Name',validators=[DataRequired(),Length(min=3,max=20)])
    lname = StringField('Last Name',validators=[DataRequired(),Length(min=3,max=20)])
    email = StringField('Email',validators=[DataRequired(),Email(),Length(min=6,max=50)])
    city = StringField('City',validators=[DataRequired(),Length(min=3,max=30)])
    password = PasswordField('Password',validators=[DataRequired(),Length(min=8,max=20)])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(),Length(min=8,max=20),EqualTo('password')])
    submit = SubmitField('Sign Up')
    
class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Email()])
    password = PasswordField('Password',validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
    
class RequestResetForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(),Length(min=8,max=20)])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
   